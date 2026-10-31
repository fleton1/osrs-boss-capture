#!/usr/bin/env python3
"""Remove personal details from captures before sharing them.

    python3 tools/scrub.py IN.jsonl[.gz] OUT.jsonl.gz

Player names in chat and in NPCs' speech become "Player".  Kill counts, personal bests and running
totals become "#", so a capture can't be matched to an account on the hiscores.  The session
timestamp is cut to its date.

Text is published only if it is known safe: its shape is in tools/known_lines.txt, or it is one of
the item messages below.  Anything else is replaced with "[unreviewed line]" and printed to stderr,
because a new line could hold a player's name that no pattern would catch.  To allow one, read it,
then add its shape to known_lines.txt (tags removed, numbers as #).  Chat from other players is
dropped outright.
"""
import gzip
import json
import os
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


# The Gemstone Crab names its top three damage dealers when it burrows.
CRAB_TOP = re.compile(r"(The top three crab crushers were ).+?(!)")


def scrub_text(chat_type, text):
    text = DROP.sub(lambda m: m.group(1) + "Player" + m.group(3), text)
    text = scrub_totals(text)
    text = CRAB_TOP.sub(r"\1Player, Player & Player\2", text)
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


KNOWN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "known_lines.txt")
UNREVIEWED = "[unreviewed line]"
CHAT_TYPES = ("SPAM", "GAMEMESSAGE", "ENGINE", "MESBOX", "DIALOG")
TAGS = re.compile(r"<[^>]+>|@\w+@")
NUMBER = re.compile(r"\d[\d,]*")
ITEM = r"[A-Za-z0-9#' ()+.\-/]+"
# Messages whose only free text is an item's name.
ITEM_LINES = re.compile(
    rf"^(?:Player received a drop: {ITEM}|Valuable drop: {ITEM}|Untradeable drop: {ITEM}"
    rf"|You found some loot: {ITEM}|You eat the {ITEM}\.|You drink some of your {ITEM}\.?)$"
)


def shape(text):
    return NUMBER.sub("#", TAGS.sub("", text))


def load_known():
    with open(KNOWN_FILE, encoding="utf-8") as f:
        return {line.rstrip("\n") for line in f if line.strip()}


def is_known(text, known):
    s = shape(text)
    return not s.strip() or s in known or bool(ITEM_LINES.match(s))


def main(src, dst):
    known = load_known()
    opener = gzip.open if src.endswith(".gz") else open
    out = []
    with opener(src, "rt", encoding="utf-8") as f:
        for line in f:
            d = scrub_line(json.loads(line))
            if d.get("type") == "chat" and d.get("chatType") not in CHAT_TYPES:
                continue
            if d.get("type") in ("chat", "overhead_text") and not is_known(d.get("text", ""), known):
                print("unreviewed:", shape(d.get("text", "")), file=sys.stderr)
                d["text"] = UNREVIEWED
            out.append(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
    # mtime=0 and no name in the header: gzip stores neither the time nor the path
    with open(dst, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as z:
        z.write(("\n".join(out) + "\n").encode("utf-8"))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
