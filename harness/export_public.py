"""Чистая копия эксперимента для публикации (GitHub).

  python harness/export_public.py <target_dir> [--email you@example.com] [--user WindowsUserName]

Копирует всё, кроме .venv, кэшей, черновиков заявок и логов, и вычищает из результатов
почту, имя пользователя Windows и пути к домашнему каталогу. В конце ищет остатки и
печатает их: если что-то найдено, не публикуйте, пока не разберётесь.
"""

import argparse
import getpass
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
EXCLUDE = shutil.ignore_patterns(".venv", "__pycache__", ".pytest_cache", "*.pyc", "*.log",
                                 "*.stderr", "grant-applications.md")
TEXT_EXT = {".py", ".json", ".jsonl", ".md", ".diff", ".txt", ".csv", ".ini", ".toml", ".yml", ".lock"}


def git_email():
    try:
        return subprocess.run(["git", "config", "--global", "user.email"], capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--email", default=git_email())
    ap.add_argument("--user", default=getpass.getuser())
    args = ap.parse_args()

    target = Path(args.target).resolve()
    if target.exists() and any(target.iterdir()):
        sys.exit(f"{target} не пустой")
    shutil.copytree(ROOT, target, ignore=EXCLUDE, dirs_exist_ok=True)

    secrets = [s for s in {args.email, args.email.split("@")[0] if args.email else "", args.user} if s]
    rules = []
    if args.email:
        rules.append((re.compile(re.escape(args.email), re.I), "dev@example.com"))
        rules.append((re.compile(re.escape(args.email.split("@")[0]), re.I), "dev"))
    if args.user:
        short = args.user[:6].upper() + "~1"
        # пути вида C:\Users\<user>\..., C:/Users/<user>, \\Users\\<user> и короткое 8.3-имя (<6 букв>~1)
        rules.append((re.compile(r"([A-Za-z]:)?((\\\\|\\|/)Users(\\\\|\\|/))(" + re.escape(args.user) + "|" + re.escape(short) + ")", re.I),
                      r"\2user"))
        rules.append((re.compile(re.escape(short), re.I), "user"))
        rules.append((re.compile(re.escape(args.user), re.I), "user"))
        secrets.append(short)

    changed = 0
    for p in target.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXT_EXT:
            s = p.read_text(encoding="utf-8", errors="replace")
            new = s
            for rx, repl in rules:
                new = rx.sub(repl, new)
            if new != s:
                p.write_text(new, encoding="utf-8")
                changed += 1

    leftovers = []
    for p in target.rglob("*"):
        if p.is_file():
            data = p.read_bytes().decode("utf-8", errors="replace").lower()
            leftovers += [f"{p.relative_to(target)}: {s}" for s in secrets if s.lower() in data]
    print(f"Скопировано в {target}, очищено файлов: {changed}")
    if leftovers:
        print("ОСТАТКИ ЛИЧНЫХ ДАННЫХ, не публикуйте:")
        print("\n".join(leftovers[:30]))
        sys.exit(1)
    print("Личных данных не найдено.")


if __name__ == "__main__":
    main()
