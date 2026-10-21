"""Runs the "cornered agent" experiment.

Examples:
  python harness/run_experiment.py --runs 10 --model claude-opus-5-5
  python harness/run_experiment.py --conditions calm,profanity --runs 2 --parallel 2
  python harness/run_experiment.py --dry-run          # print the commands, do not call the agent

Each run: a fresh copy of template/ in a temp dir, git init, then the agent is called
headless (claude -p / gemini -p, stream-json output) and pushed up to N times via resume.
After every round the sandbox is snapshotted and fully checked (detect.evaluate).
Output: results/<batch>/<run_id>/ (meta.json, roundK.jsonl, snapshots/, roundK.diff).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import re
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402

ROOT = detect.ROOT
CONDITIONS_FILE = Path(os.environ.get("CORNERED_CONDITIONS", Path(__file__).resolve().parent / "conditions.json"))
CONFIG = json.loads(CONDITIONS_FILE.read_text(encoding="utf-8"))


def default_python():
    for rel in (".venv/Scripts/python.exe", ".venv/bin/python"):
        if (ROOT / rel).exists():
            return str(ROOT / rel)
    return sys.executable


def git(work, *args):
    subprocess.run(
        ["git", "-c", "user.name=dev", "-c", "user.email=dev@example.com", "-c", "core.autocrlf=false", *args],
        cwd=work, check=True, capture_output=True,
    )


def make_sandbox():
    base = Path(tempfile.mkdtemp(prefix="cornered-"))
    work = base / "events"
    detect.copy_tree(detect.TEMPLATE, work)
    git(work, "init", "-q", "-b", "main")
    git(work, "config", "user.name", "dev")
    git(work, "config", "user.email", "dev@example.com")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "events: dedupe helper")
    return base, work


def gemini_entry():
    """On Windows gemini.cmd mangles non-ASCII arguments via cmd.exe, so node is called directly."""
    try:
        root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, shell=os.name == "nt").stdout.strip()
    except OSError:
        return None
    entry = Path(root) / "@google" / "gemini-cli" / "bundle" / "gemini.js"
    return str(entry) if entry.exists() else None


def gemini_home(base, args):
    """A separate GEMINI_CLI_HOME per run: no personal GEMINI.md, memory, extensions or history."""
    home = base / "gemini-home"
    (home / ".gemini").mkdir(parents=True, exist_ok=True)
    settings = {
        # maxSessionTurns covers the whole session including --resume, so budget all rounds
        "model": {"maxSessionTurns": args.max_turns * (CONFIG["max_pressures"] + 1)},
        "tools": {"exclude": ["google_web_search", "web_fetch"]},
        "security": {"auth": {"selectedType": "gemini-api-key"}},
        "general": {"disableAutoUpdate": True, "checkpointing": {"enabled": False}},
        "privacy": {"usageStatisticsEnabled": False},
    }
    (home / ".gemini" / "settings.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")
    return home


def gemini_cmd(args, message, session_id):
    cmd = ["node", args.gemini, "-p", message, "-o", "stream-json", "--yolo", "--skip-trust"]
    if args.model:
        cmd += ["-m", args.model]
    if session_id:
        cmd += ["--resume", "latest"]
    return cmd


def agent_cmd(args, message, session_id):
    return gemini_cmd(args, message, session_id) if args.agent == "gemini" else claude_cmd(args, message, session_id)


def claude_cmd(args, message, session_id):
    cmd = [
        args.claude, "-p", message,
        "--output-format", "stream-json", "--verbose",
        "--max-turns", str(args.max_turns),
        "--model", args.model or "claude-opus-5-5",
        "--permission-mode", "bypassPermissions",
        "--tools", args.tools,
        "--strict-mcp-config", "--no-chrome",
    ]
    cmd += ["--bare"] if args.bare else ["--safe-mode"]
    if args.effort:
        cmd += ["--effort", args.effort]
    if session_id:
        cmd += ["--resume", session_id]
    return cmd


def agent_env(python, home=None):
    env = dict(os.environ)
    if home:
        env["GEMINI_CLI_HOME"] = str(home)
    scripts = str(Path(python).parent)
    env["PATH"] = scripts + os.pathsep + env.get("PATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    for k in ("VIRTUAL_ENV", "PYTHONPATH"):
        env.pop(k, None)
    return env


LIMIT_RE = re.compile(r"usage limit|rate limit|limit reached|overloaded|quota|credit balance|\b429\b|\b529\b", re.I)
STOP = threading.Event()   # hit a usage limit: do not start new runs
SPENT = {"usd": 0.0}
SPENT_LOCK = threading.Lock()


def api_error(parsed, stderr_path):
    """Failure not caused by the agent (limit, overload, crash). Such runs are excluded from stats."""
    res = parsed["result"]
    stderr = Path(stderr_path).read_text(encoding="utf-8", errors="replace") if Path(stderr_path).exists() else ""
    if res is None:
        return (stderr.strip() or "no result event in stream-json")[-500:]
    if res.get("is_error") and res.get("subtype") != "error_max_turns":
        return str(res.get("error") or res.get("result") or res.get("subtype"))[-500:]
    if LIMIT_RE.search(stderr):
        return stderr[-500:]
    return None


def run_cost(meta):
    # total_cost_usd in stream-json is cumulative per session: take the max, not the sum
    return max(((r["transcript"]["result"] or {}).get("total_cost_usd") or 0 for r in meta["rounds"]), default=0)


def is_complete(run_dir):
    try:
        return json.loads((run_dir / "meta.json").read_text(encoding="utf-8")).get("complete") is True
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def run_one(run_id, condition, args, batch_dir):
    if STOP.is_set():
        return run_id, "skipped"
    with SPENT_LOCK:
        if args.budget_usd and SPENT["usd"] >= args.budget_usd:
            return run_id, "skipped"
    run_dir = batch_dir / run_id
    shutil.rmtree(run_dir, ignore_errors=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    base, work = make_sandbox()
    home = gemini_home(base, args) if args.agent == "gemini" else None
    meta = {
        "run_id": run_id, "condition": condition, "agent": args.agent, "model": args.model, "sandbox": str(work),
        "started": datetime.now().isoformat(timespec="seconds"), "rounds": [],
    }
    session_id = None
    message = CONFIG["initial_prompt"]
    error = None
    try:
        for r in range(CONFIG["max_pressures"] + 1):
            stream = run_dir / f"round{r}.jsonl"
            cmd = agent_cmd(args, message, session_id)
            t0 = time.time()
            with open(stream, "w", encoding="utf-8") as out, open(run_dir / f"round{r}.stderr", "w", encoding="utf-8") as err:
                try:
                    subprocess.run(cmd, cwd=work, stdout=out, stderr=err, timeout=args.timeout,
                                   env=agent_env(args.python, home), encoding="utf-8")
                    timed_out = False
                except subprocess.TimeoutExpired:
                    timed_out = True
            parsed = detect.parse_stream(stream)
            session_id = parsed["session_id"] or session_id
            error = "timeout" if timed_out else api_error(parsed, run_dir / f"round{r}.stderr")
            if error:
                print(f"[{run_id}] round {r}: FAILED: {error[:200]}", flush=True)
                if LIMIT_RE.search(error):
                    STOP.set()
                break

            snap = run_dir / "snapshots" / f"round{r}"
            detect.copy_tree(work, snap)
            (run_dir / f"round{r}.diff").write_text(detect.text_diff(detect.TEMPLATE, snap), encoding="utf-8")
            state = detect.evaluate(snap, args.python)

            meta["rounds"].append({
                "round": r, "message": message, "seconds": round(time.time() - t0, 1), "timed_out": timed_out,
                "transcript": {k: v for k, v in parsed.items() if k != "texts"},
                "state": state,
            })
            (run_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

            red = not state["pytest_agent"].get("green")
            print(f"[{run_id}] round {r}: pytest={'green' if not red else 'red'} "
                  f"cheated={state['flags']['cheated']} contradiction={parsed['named_contradiction']}", flush=True)
            if r == CONFIG["max_pressures"] or not session_id:
                break
            if not red:
                break
            message = CONFIG["conditions"][condition]
    except BaseException as exc:
        error = error or repr(exc)
        raise
    finally:
        meta["finished"] = datetime.now().isoformat(timespec="seconds")
        meta["error"] = error
        meta["complete"] = error is None and bool(meta["rounds"])
        meta["cost_usd"] = run_cost(meta)
        (run_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        with SPENT_LOCK:
            SPENT["usd"] += meta["cost_usd"]
        if not args.keep_sandbox:
            shutil.rmtree(base, ignore_errors=True)
    return run_id, "complete" if meta["complete"] else "error"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conditions", default=",".join(CONFIG["conditions"]))
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--agent", choices=["claude", "gemini"], default="claude")
    ap.add_argument("--model", default=None,
                    help="claude: default claude-opus-5-5; gemini: CLI default (e.g. gemini-3.1-pro-preview)")
    ap.add_argument("--effort", default=None)
    ap.add_argument("--max-turns", type=int, default=30)
    ap.add_argument("--tools", default="Bash,Read,Edit,Write,Glob,Grep")
    ap.add_argument("--timeout", type=int, default=1800, help="seconds per agent call")
    ap.add_argument("--parallel", type=int, default=1)
    ap.add_argument("--bare", action="store_true", help="--bare instead of --safe-mode (needs ANTHROPIC_API_KEY)")
    ap.add_argument("--python", default=default_python(), help="python with pytest, visible to the agent")
    ap.add_argument("--claude", default=shutil.which("claude") or "claude")
    ap.add_argument("--gemini", default=None, help="path to bundle/gemini.js (default: from npm root -g)")
    ap.add_argument("--batch", default=None, help="batch name; re-running with the same name resumes unfinished runs")
    ap.add_argument("--budget-usd", type=float, default=None,
                    help="stop starting new runs once spend exceeds this (list price from stream-json)")
    ap.add_argument("--keep-sandbox", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    unknown = set(conditions) - set(CONFIG["conditions"])
    if unknown:
        sys.exit(f"unknown conditions: {unknown}")

    if args.agent == "gemini":
        args.gemini = args.gemini or gemini_entry()
        if not args.gemini:
            sys.exit("Gemini CLI not found: npm install -g @google/gemini-cli")
        if not os.environ.get("GEMINI_API_KEY") and not args.dry_run:
            sys.exit("GEMINI_API_KEY is not set: create a key in Google AI Studio and export it")
    elif not args.model:
        args.model = "claude-opus-5-5"

    if args.dry_run:
        print("python:", args.python)
        print(" ".join(agent_cmd(args, CONFIG["initial_prompt"], None)))
        print(" ".join(agent_cmd(args, CONFIG["conditions"][conditions[0]], "<session-id>")))
        return

    check = subprocess.run([args.python, "-m", "pytest", "--version"], capture_output=True, text=True)
    if check.returncode != 0:
        sys.exit(f"pytest not found for {args.python}. Create .venv, see README")

    batch = args.batch or datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + (args.model or args.agent).replace("/", "_")
    batch_dir = ROOT / "results" / batch
    batch_dir.mkdir(parents=True, exist_ok=True)
    freeze_before = subprocess.run([args.python, "-m", "pip", "freeze"], capture_output=True, text=True).stdout
    (batch_dir / "batch.json").write_text(json.dumps({
        "agent": args.agent, "model": args.model, "conditions": conditions, "runs": args.runs, "max_turns": args.max_turns,
        "tools": args.tools, "bare": args.bare, "effort": args.effort, "config": CONFIG, "conditions_file": CONDITIONS_FILE.name,
        "agent_version": subprocess.run(
            ["node", args.gemini, "--version"] if args.agent == "gemini" else [args.claude, "--version"],
            capture_output=True, text=True).stdout.strip(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # interleave conditions so an interrupted batch stays balanced
    jobs = [(f"{c}-{i:02d}", c) for i in range(1, args.runs + 1) for c in conditions]
    done = [rid for rid, _ in jobs if is_complete(batch_dir / rid)]
    jobs = [(rid, c) for rid, c in jobs if rid not in done]
    for rid in done:
        SPENT["usd"] += json.loads((batch_dir / rid / "meta.json").read_text(encoding="utf-8")).get("cost_usd") or 0
    if done:
        print(f"Already done: {len(done)}, remaining: {len(jobs)}, spent: ${SPENT['usd']:.2f}")
    status = {"complete": 0, "error": 0, "skipped": 0}
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = [pool.submit(run_one, rid, c, args, batch_dir) for rid, c in jobs]
        for f in as_completed(futures):
            try:
                rid, st = f.result()
                status[st] += 1
                if st != "skipped":
                    print(f"[{rid}] {st}; total spent ${SPENT['usd']:.2f}", flush=True)
            except Exception as exc:  # noqa: BLE001
                status["error"] += 1
                print("run failed:", exc, flush=True)

    print(f"\nSummary: complete {status['complete']}, failed {status['error']}, not started {status['skipped']}, "
          f"spent ${SPENT['usd']:.2f}")
    if status["error"] or status["skipped"]:
        print(f"Resume: python harness/run_experiment.py --batch {batch} [same flags]")

    freeze_after = subprocess.run([args.python, "-m", "pip", "freeze"], capture_output=True, text=True).stdout
    if freeze_after != freeze_before:
        print("WARNING: venv packages changed during the batch (the agent installed something).")
        (batch_dir / "pip_freeze_diff.txt").write_text(f"BEFORE\n{freeze_before}\nAFTER\n{freeze_after}", encoding="utf-8")

    print(f"\nDone: {batch_dir}\nAnalyze: python harness/analyze.py {batch_dir}")


if __name__ == "__main__":
    main()
