#!/usr/bin/env python3
"""Rebuild the README's boss checklist from the plugin's boss list and data/captures.

    python3 tools/update_checklist.py

The list between the two markers in README.md is generated: don't edit it by hand.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = "src/main/java/io/github/fleton1/bosscapture/BossCaptureConfig.java"
START = "<!-- checklist:start -->"
END = "<!-- checklist:end -->"
# Names in the plugin's list that are one fight here.
SAME_FIGHT = {"Dusk": "Grotesque Guardians", "Dawn": "Grotesque Guardians"}
# Fights recorded but not in the plugin's default list: name -> capture file prefixes or folder.
EXTRA = {"Barrows Brothers": "barrows/", "Crazy Archaeologist": "crazy-archaeologist"}
# Whole recordings that span several fights.
OTHER = ("manual-", "fullrun-")


def boss_names():
    with open(os.path.join(ROOT, CONFIG), encoding="utf-8") as f:
        source = f.read()
    body = re.search(r"String bossNames\(\)\s*\{\s*return(.*?);", source, re.S).group(1)
    text = "".join(re.findall(r'"([^"]*)"', body))
    names = {SAME_FIGHT.get(n.strip(), n.strip()) for n in text.split(",") if n.strip()}
    return sorted(names | set(EXTRA), key=str.lower)


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower().replace("'", "")).strip("-")


def captures():
    base = os.path.join(ROOT, "data/captures")
    return [f"{d}/{f}" for d in sorted(os.listdir(base)) for f in sorted(os.listdir(os.path.join(base, d)))]


def count(name, files):
    key = EXTRA.get(name)
    if key and key.endswith("/"):
        return sum(f.startswith(key) for f in files)
    prefix = key or slug(name)
    return sum(re.match(re.escape(prefix) + r"-(?:group-|solo-)?20\d{6}", f.split("/")[1]) is not None for f in files)


def checklist():
    files = captures()
    names = boss_names()
    counts = {n: count(n, files) for n in names}
    done = sum(1 for c in counts.values() if c)
    lines = [f"**{done} of {len(names)} captured**, {len(files)} recordings in all.", ""]
    for n in names:
        c = counts[n]
        lines.append(f"- [x] {n} ({c})" if c else f"- [ ] {n}")
    other = sum(f.split("/")[1].startswith(OTHER) for f in files)
    if other:
        lines += ["", f"Plus {other} longer recording(s) that span several fights."]
    return "\n".join(lines)


def main():
    path = os.path.join(ROOT, "README.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    a, b = text.index(START) + len(START), text.index(END)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text[:a] + "\n" + checklist() + "\n" + text[b:])


if __name__ == "__main__":
    main()
