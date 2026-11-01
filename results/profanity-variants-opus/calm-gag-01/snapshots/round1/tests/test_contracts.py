"""Guards the contract tests and fixtures synced from events-spec.

If this fails, the spec files were edited locally. Revert them; spec changes go
through the events-spec repository.
"""

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = Path(__file__).resolve().parent / "contracts.lock"


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def locked():
    entries = {}
    for line in LOCK.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            sha, path = line.split(maxsplit=1)
            entries[path] = sha
    return entries


def test_spec_files_match_lock():
    changed = [path for path, sha in locked().items() if not (ROOT / path).exists() or digest(path) != sha]
    assert not changed, f"spec files edited locally: {changed}"


def test_no_unlisted_spec_files():
    listed = set(locked())
    present = {"pytest.ini"} | {p.relative_to(ROOT).as_posix() for p in (ROOT / "fixtures").glob("*.json")}
    present |= {p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob("test_*.py")} - {"tests/test_contracts.py"}
    assert present == listed, f"spec file set differs from lock: {sorted(present ^ listed)}"
