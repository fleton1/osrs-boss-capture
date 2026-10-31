#!/usr/bin/env python3
"""Remove personal details from captures before sharing them.

    python3 tools/scrub.py IN.jsonl[.gz] OUT.jsonl.gz

Replaces player names in chat and in NPCs' speech with "Player", and cuts the session
timestamp to its date.  Fails on a line holding a no-break space (a two-word name) or on chat
from other players.  A one-word name in an NPC line it does not know gets through, so read
the overhead_text lines of a new capture before you share it.
Kill counts, personal bests and running totals become "#", so a capture can't be matched to an
account on the hiscores.  The messages stay, since they mark when a kill happened.
"""
import gzip
import json
import re
import sys

DROP = re.compile(r"^((?:<col=[0-9a-fA-F]+>)?)(.+?)( received a drop:)")
NBSP = " "
# Random-event NPCs say nearby players' names out loud.  Each pattern keeps the line and drops the name.
SPOKEN = [re.compile(p) for p in (
    r"^(Greetings )(.+)(, I need your help\.)$",
    r"^(Greetings from the frog prince, )(.+)(!)$",
    r"^(Hello, )(?:Master )?(.+?)(, are you there\?|\?)$",
    r"^(I have come to check you, )(.+)(\.\.\.)$",
    r"^(Please let me check you, )(.+)(!)$",
    r"^(I'd like to talk to you, )(.+)(!)$",
    r"^()(.+)(\? Are you there\?)$",
    r"^(Come on )(.+)(, I made these specially!)$",
)]


def scrub_spoken(text):
    for pattern in SPOKEN:
        text = pattern.sub(lambda m: m.group(1) + "Player" + m.group(3), text)
    return text


# The number after each of these is the player's own running total.
TOTALS = re.compile(
    r"((?:kill count is|Lunar Chest count is|subdued Wintertodt count is|[Cc]ount is"
    r"|Personal best|Total permits|You're now owed)[: ]*(?:<col=[0-9a-fA-F]+>)?)\d[\d,:.]*"
)
OWED = re.compile(r"(You're owed an additional )\d[\d,]*")


def scrub_totals(text):
    return OWED.sub(r"\1#", TOTALS.sub(r"\1#", text))


def scrub_text(chat_type, text):
    text = DROP.sub(lambda m: m.group(1) + "Player" + m.group(3), text)
    text = scrub_totals(text)
    if chat_type == "DIALOG" and "|" in text:
        speaker, rest = text.split("|", 1)
        if NBSP in speaker:
            speaker = "Player"
        text = speaker + "|" + rest
    return text


def scrub_line(d):
    if d.get("type") == "session" and "started" in d:
        d["started"] = d["started"][:10]
    if d.get("type") == "chat":
        d["text"] = scrub_text(d.get("chatType"), d.get("text", ""))
    if d.get("type") == "overhead_text":
        d["text"] = scrub_spoken(d.get("text", ""))
    return d


def main(src, dst):
    opener = gzip.open if src.endswith(".gz") else open
    out = []
    with opener(src, "rt", encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            d = scrub_line(json.loads(line))
            if d.get("type") in ("chat", "overhead_text") and NBSP in d.get("text", ""):
                sys.exit(f"{src}:{n}: possible player name left: {d['text']!r}")
            if d.get("type") == "chat" and d.get("chatType") not in (
                "SPAM", "GAMEMESSAGE", "ENGINE", "MESBOX", "DIALOG",
            ):
                sys.exit(f"{src}:{n}: chat from other players must not be shared: {d.get('chatType')}")
            out.append(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
    # mtime=0 and no name in the header: gzip stores neither the time nor the path
    with open(dst, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as z:
        z.write(("\n".join(out) + "\n").encode("utf-8"))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
