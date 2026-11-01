"""Render each run's conversation with the agent as readable files.

  python harness/export_chats.py results/<batch> [results/<batch2> ...]

Writes results/<batch>/chats/<run_id>.md: per round the user's message, the agent's text,
thinking (when the stream has it), tool calls with their results (trimmed), and the round's state.
Also writes results/<batch>/chats/<run_id>.txt: the same conversation as plain text with nothing
trimmed, and results/<batch>/chats/all.txt with every run of the batch in one file.
"""

import csv
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MAX_INPUT = 1500
MAX_RESULT = 1200


def trim(text, limit):
    text = text if isinstance(text, str) else json.dumps(text, ensure_ascii=False, indent=1)
    return text if len(text) <= limit else text[:limit] + f"\n… [{len(text) - limit} more chars]"


def fence(text):
    ticks = "````" if "```" in text else "```"
    return f"{ticks}\n{text}\n{ticks}"


def tool_input(name, inp):
    if not isinstance(inp, dict):
        return trim(inp, MAX_INPUT)
    if "command" in inp:
        return trim(str(inp["command"]), MAX_INPUT)
    if set(inp) <= {"file_path", "path", "pattern"}:
        return trim(" ".join(str(v) for v in inp.values()), MAX_INPUT)
    return trim(inp, MAX_INPUT)


def result_text(content):
    if isinstance(content, list):
        content = "\n".join(c.get("text", "") if isinstance(c, dict) else str(c) for c in content)
    return trim(str(content or ""), MAX_RESULT)


def render_claude(lines, out):
    for e in lines:
        t = e.get("type")
        if t == "assistant":
            for b in e["message"].get("content", []):
                if b["type"] == "text" and b["text"].strip():
                    out.append(f"**Agent:**\n\n{b['text'].strip()}\n")
                elif b["type"] == "thinking" and b.get("thinking", "").strip():
                    body = "\n".join("> " + s for s in b["thinking"].strip().splitlines())
                    out.append(f"*Thinking:*\n\n{body}\n")
                elif b["type"] == "tool_use":
                    out.append(f"`{b['name']}`\n\n{fence(tool_input(b['name'], b.get('input')))}\n")
        elif t == "user" and isinstance(e["message"].get("content"), list):
            for b in e["message"]["content"]:
                if b.get("type") == "tool_result":
                    tag = " (error)" if b.get("is_error") else ""
                    out.append(f"<details><summary>result{tag}</summary>\n\n{fence(result_text(b.get('content')))}\n\n</details>\n")
        elif t == "result":
            out.append(f"*Round end: {e.get('subtype')}, turns {e.get('num_turns')}, cumulative cost ${e.get('total_cost_usd') or 0:.4f}*\n")


def render_gemini(lines, out):
    buf = []

    def flush():
        if buf:
            out.append(f"**Agent:**\n\n{''.join(buf).strip()}\n")
            buf.clear()

    for e in lines:
        t = e.get("type")
        if t == "message" and e.get("role") == "assistant":
            buf.append(e.get("content", ""))
        elif t == "tool_use":
            flush()
            out.append(f"`{e.get('tool_name')}`\n\n{fence(tool_input(e.get('tool_name'), e.get('parameters')))}\n")
        elif t == "tool_result":
            out.append(f"<details><summary>result ({e.get('status')})</summary>\n\n{fence(result_text(e.get('output')))}\n\n</details>\n")
        elif t == "error":
            flush()
            out.append(f"*Error: {e.get('message')}*\n")
        elif t == "result":
            flush()
            out.append(f"*Round end: {e.get('status')}*\n")
    flush()


def plain(lines):
    """The conversation as plain text, untrimmed: (label, text) pairs."""
    out = []
    for e in lines:
        t = e.get("type")
        if t == "assistant":
            for b in e["message"].get("content", []):
                if b["type"] == "text" and b["text"].strip():
                    out.append(("AGENT", b["text"].strip()))
                elif b["type"] == "thinking" and b.get("thinking", "").strip():
                    out.append(("AGENT THINKING", b["thinking"].strip()))
                elif b["type"] == "tool_use":
                    inp = b.get("input")
                    body = inp["command"] if isinstance(inp, dict) and "command" in inp else json.dumps(inp, ensure_ascii=False, indent=1)
                    out.append((f"TOOL {b['name']}", body))
        elif t == "user" and isinstance(e["message"].get("content"), list):
            for b in e["message"]["content"]:
                if b.get("type") == "tool_result":
                    c = b.get("content")
                    if isinstance(c, list):
                        c = "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in c)
                    out.append(("OUTPUT" + (" (error)" if b.get("is_error") else ""), str(c or "").rstrip()))
        elif t == "message" and e.get("role") == "assistant":
            if out and out[-1][0] == "AGENT":
                out[-1] = ("AGENT", out[-1][1] + e.get("content", ""))
            else:
                out.append(("AGENT", e.get("content", "")))
        elif t == "tool_use":
            out.append((f"TOOL {e.get('tool_name')}", json.dumps(e.get("parameters"), ensure_ascii=False, indent=1)))
        elif t == "tool_result":
            out.append((f"OUTPUT ({e.get('status')})", str(e.get("output") or "").rstrip()))
        elif t == "error":
            out.append(("ERROR", str(e.get("message"))))
    return out


def counts(p):
    total = p.get("tests")
    if not total:
        return "no result"
    bad = (p.get("failures") or 0) + (p.get("errors") or 0)
    text = f"{total - bad - (p.get('skipped') or 0)}/{total} passed"
    if p.get("failed"):
        text += "; failed: " + ", ".join(t.split("::")[-1] for t in p["failed"])
    return text


def state_line(state):
    if not state:
        return ""
    f = state.get("flags", {})
    raised = [k for k, v in f.items() if v is True]
    ref = state.get("pytest_reference", {})
    agent = state.get("pytest_agent", {})
    return (f"*State after round: agent pytest {'green' if agent.get('green') else 'red'}"
            f" ({counts(agent)}), reference pytest {'green' if ref.get('green') else 'red'}"
            f"; flags: {', '.join(raised) or 'none'}*\n")


def export(batch):
    summary = {}
    if (batch / "summary.csv").exists():
        with open(batch / "summary.csv", encoding="utf-8-sig") as f:
            summary = {r["run_id"]: r for r in csv.DictReader(f)}
    out_dir = batch / "chats"
    out_dir.mkdir(exist_ok=True)
    n = 0
    everything = []
    for meta_path in sorted(batch.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        run = meta_path.parent
        s = summary.get(meta["run_id"], {})
        out = [f"# {meta['run_id']}", "",
               f"- agent: {meta.get('agent', 'claude')}, model: {meta.get('model')}",
               f"- condition: {meta['condition']}"]
        if s:
            out += [f"- outcome: **{s['outcome']}**" + (f" ({s['cheat_kind']}, round {s['cheat_round']})" if s.get("cheat_kind") else ""),
                    f"- cost: ${s.get('cost_usd')}"]
            if s.get("manual_review"):
                out.append(f"- manual review: {s['manual_review']}")
        out.append("")
        txt = [f"RUN {meta['run_id']} | model {meta.get('model')} | condition {meta['condition']}"
               + (f" | outcome {s['outcome']}" if s else ""), ""]
        for r in meta["rounds"]:
            k = r["round"]
            out += ["---", "", f"## Round {k}" + (" (initial prompt)" if k == 0 else f" (push {k})"), "",
                    f"**User:** {r.get('message', '')}", ""]
            stream = run / f"round{k}.jsonl"
            lines = []
            if stream.exists():
                for line in stream.read_text(encoding="utf-8").splitlines():
                    try:
                        lines.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            if any(e.get("type") == "assistant" for e in lines):
                render_claude(lines, out)
            else:
                render_gemini(lines, out)
            out.append(state_line(r.get("state")))
            txt += ["=" * 80, f"ROUND {k}", "=" * 80, "", f"USER:\n{r.get('message', '')}", ""]
            txt += [f"{label}:\n{body}\n" for label, body in plain(lines)]
            txt += [state_line(r.get("state")).strip("*\n"), ""]
        (out_dir / f"{meta['run_id']}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
        (out_dir / f"{meta['run_id']}.txt").write_text("\n".join(txt) + "\n", encoding="utf-8")
        everything.append("\n".join(txt))
        n += 1
    (out_dir / "all.txt").write_text(("\n\n" + "#" * 80 + "\n\n").join(everything) + "\n", encoding="utf-8")
    print(f"{batch}: {n} chats -> {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arg in sys.argv[1:]:
        export(Path(arg))
