#!/usr/bin/env python3
"""Check that every capture in data/captures is safe to publish.  CI runs this on pull requests.

    python3 tools/check_captures.py [--known FILE]

Exits non-zero and names each problem.  --known checks against another copy of the allowlist,
which is how CI stops a pull request from approving its own text.
"""
import argparse
import gzip
import json
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrub  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = re.compile(r"^[a-z0-9-]+-20\d{6}-\d\d\.jsonl\.gz$")
MAX_BYTES = 20 * 1024 * 1024
TOTAL = re.compile(
    r"(?:[Cc]ount is|Personal best|Total permits|You're now owed)[: ]*(?:<col=[0-9a-fA-F]+>)?\d"
    r"|You're owed an additional \d"
)
TYPES = {
    "session", "tick", "equipment", "end", "death", "chat", "overhead_text", "hitsplat", "anim", "spotanim",
    "projectile", "graphics_object", "interact", "npc_spawn", "npc_despawn", "npc_change", "object_spawn",
    "object_despawn",
}


def check_lines(lines, known):
    """The problems in one capture's lines, at most one of each kind per text."""
    problems = []
    seen_session = False
    for n, line in enumerate(lines, 1):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            problems.append(f"line {n}: not JSON")
            continue
        kind = d.get("type")
        if kind not in TYPES:
            problems.append(f"line {n}: unknown event type {kind!r}")
        if kind == "session":
            seen_session = True
            if not re.fullmatch(r"\d{4}-\d\d-\d\d", str(d.get("started", ""))):
                problems.append(f"line {n}: session time must be a date only (not scrubbed?)")
        if kind == "chat" and d.get("chatType") not in scrub.CHAT_TYPES:
            problems.append(f"line {n}: chat from other players ({d.get('chatType')})")
        if kind in ("chat", "overhead_text"):
            text = d.get("text", "")
            if text == scrub.UNREVIEWED:
                continue
            if TOTAL.search(text):
                problems.append(f"line {n}: kill count or running total: {scrub.shape(text)!r}")
            elif not scrub.is_known(text, known):
                problems.append(f"line {n}: unreviewed text: {scrub.shape(text)!r}")
    if not seen_session:
        problems.append("no session line")
    return problems


def check_file(path, known):
    name = os.path.basename(path)
    if not NAME.match(name):
        return [f"file name must look like vorkath-20261031-01.jsonl.gz, not {name}"]
    if os.path.getsize(path) > MAX_BYTES:
        return ["larger than 20 MB: record one or two kills"]
    try:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return check_lines(f, known)
    except OSError as e:
        return [f"can't read it as gzip: {e}"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--known", default=scrub.KNOWN_FILE)
    args = parser.parse_args()
    with open(args.known, encoding="utf-8") as f:
        known = {line.rstrip("\n") for line in f if line.strip()}
    base = os.path.join(ROOT, "data/captures")
    bad = checked = 0
    for folder, _, files in sorted(os.walk(base)):
        for name in sorted(files):
            path = os.path.join(folder, name)
            rel = os.path.relpath(path, ROOT)
            checked += 1
            problems = check_file(path, known)
            if problems:
                bad += 1
                print(f"{rel}: {len(problems)} problem(s)")
                for p in problems[:15]:
                    print("  " + p)
    print(f"checked {checked} captures, {bad} with problems")
    if bad:
        print("Run tools/scrub.py on the raw recording. See CONTRIBUTING.md.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
