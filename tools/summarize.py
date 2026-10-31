#!/usr/bin/env python3
"""Summarise a Boss Capture JSONL file: NPC forms, animations with their tick gaps,
projectiles with flight times, spot anims, sounds and hitsplats.

usage: summarize.py CAPTURE.jsonl [--npc ID]
"""
import gzip
import argparse
import json
from collections import Counter, defaultdict

CYCLES_PER_TICK = 30  # client cycles are 20 ms, ticks are 600 ms


def gaps(ticks):
    d = [b - a for a, b in zip(ticks, ticks[1:])]
    return Counter(d).most_common(4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("capture")
    ap.add_argument("--npc", type=int, help="only events for this NPC id")
    args = ap.parse_args()

    names, anims, gfx, sounds, hits = {}, defaultdict(list), Counter(), Counter(), Counter()
    projs = defaultdict(list)
    forms = []
    session = end = None
    with (gzip.open(args.capture, "rt", encoding="utf-8") if str(args.capture).endswith(".gz") else open(args.capture)) as f:
        for raw in f:
            e = json.loads(raw)
            t = e["type"]
            npc_id = e.get("npcId", e.get("id"))
            if args.npc is not None and e.get("actor") == "npc" and e.get("npcId") != args.npc:
                continue
            if t == "session":
                session = e
            elif t == "end":
                end = e
            elif t == "npc_spawn":
                names[e["id"]] = e.get("name")
            elif t == "npc_change":
                names[e["to"]] = e.get("name")
                forms.append((e["tick"], e["from"], e["to"]))
            elif t == "anim" and e["anim"] != -1:
                who = "me" if e["actor"] == "me" else f"npc {e['npcId']}"
                anims[(who, e["anim"])].append(e["tick"])
            elif t == "spotanim":
                who = "me" if e["actor"] == "me" else f"npc {e['npcId']}"
                for g in e["gfx"]:
                    gfx[(who, g["id"])] += 1
            elif t == "projectile":
                src = e.get("from", {}).get("npcId", e.get("from", {}).get("actor", "?"))
                flight = (e["endCycle"] - e["startCycle"]) / CYCLES_PER_TICK
                projs[(e["id"], src)].append((e["tick"], flight))
            elif t in ("sound", "area_sound"):
                sounds[e["id"]] += 1
            elif t == "hitsplat":
                who = "me" if e["actor"] == "me" else f"npc {e['npcId']}"
                hits[who] += e["amount"]

    if session:
        print(f"{session['boss']}  rev {session['revision']}  world {session['world']}  "
              f"{session['started']}  ticks {end['ticks'] if end else '?'}")
    print("\nNPCs:", ", ".join(f"{i} {n}" for i, n in sorted(names.items())))
    if forms:
        print("\nForm changes (tick: from -> to):")
        for tick, a, b in forms:
            print(f"  {tick:>5}: {a} -> {b}")
    print("\nAnimations (who, anim: count, first tick, common gaps in ticks):")
    for (who, anim), ticks in sorted(anims.items(), key=lambda kv: kv[1][0]):
        print(f"  {who:>10} {anim:>6}: x{len(ticks):<4} first {ticks[0]:<5} gaps {gaps(ticks)}")
    print("\nProjectiles (id, source: count, flight ticks):")
    for (pid, src), shots in sorted(projs.items(), key=lambda kv: str(kv[0])):
        flights = Counter(round(f, 2) for _, f in shots).most_common(3)
        print(f"  {pid:>6} from {src}: x{len(shots):<4} flight {flights}")
    print("\nSpot anims:", ", ".join(f"{w} {g} x{c}" for (w, g), c in gfx.most_common()))
    print("\nSounds:", ", ".join(f"{s} x{c}" for s, c in sounds.most_common(30)))
    print("\nDamage taken:", dict(hits))


if __name__ == "__main__":
    main()
