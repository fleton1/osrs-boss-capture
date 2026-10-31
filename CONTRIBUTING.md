# Contributing boss data

The most useful thing you can add is a recording of a fight that isn't ticked in the
[README's checklist](README.md#capture-checklist), or a second recording of one with few.

## Record a fight

1. Build and run the plugin as the [README](README.md#how-to-use-it) describes. You need a JDK 11+.
2. Check the boss is in the plugin's **Boss names** setting, then fight it normally. One or two complete kills is plenty.
3. Find the file in `~/osrs-captures/`. For things with no boss nearby, use **Record everything**, and turn it off
   when you're done.

Don't add overlays, helpers or anything that shows during a fight. This plugin stays log-only.

## Scrub it

Raw recordings hold your display name, other players' names, your kill counts and when you played.
**Never share a raw file.**

```bash
python3 tools/scrub.py ~/osrs-captures/vorkath-20261031-141353.jsonl \
    data/captures/vorkath/vorkath-20261031-03.jsonl.gz
```

Name it `<boss>-<yyyyMMdd>-<NN>.jsonl.gz`, using the next free number for that day, with the date only and no time.
Put it in the boss's folder under `data/captures/`.

Text the scrubber hasn't seen becomes `[unreviewed line]`, and it prints each one. That's normal for a boss nobody has
recorded yet, and it's fine to submit. A recording is still useful with those lines hidden.

## Open a pull request

- Include only your `.jsonl.gz` files. Leave the README alone: its checklist updates itself after the merge.
- Don't edit `tools/known_lines.txt`. Paste the printed `unreviewed:` lines into the pull request instead, after
  removing any player names. A maintainer reads them and adds the safe ones, then they show up in later recordings.
- Say what gear and combat style you used, and whether you got the kill.

A check runs on every pull request. It fails on chat from other players, kill counts, full timestamps or text
that isn't on the allowlist. Run it yourself first: `python3 tools/check_captures.py`.

By opening a pull request, you agree your capture and any report are released under CC0 1.0 (see `LICENSE-DATA`), and
that any code is under BSD-2-Clause (see `LICENSE`).

## If something private got through

Open an issue that says which file and line, without repeating the name. It will be removed from the repo's history.
