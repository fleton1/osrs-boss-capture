# Hespori: one capture (2026-10-30)

Capture: `data/captures/hespori/hespori-20261030-180758.jsonl.gz` (one kill, 2,664 events, rev 241, instanced).
Analysed with `tools/hespori/stats.py` (run with `python3 -I`). Ticks are game ticks; the Hespori's swing is the tick its animation starts.

## Confirmed by the capture

- **Hit points: 300.** The Hespori's hitsplats sum to exactly 300.
- **Buds:** four 8584 buds at (1243,10083), (1243,10091), (1251,10083), (1251,10091), each time.
- **Buds die to one blow:** 12 kills, each a 10-damage hitsplat.
- **Flowers:** a killed bud leaves a static 8585 on its tile about 3 ticks after its death. The next phase turns the 8585s back into 8584 (same index).
- **Phases:** buds open at the fight's start, then at tick 57 (cumulative damage 137, past the 66% line) and tick 83 (cumulative 205, past the 33% line). Both re-openings happen in the same tick as the hit that crosses the line.
- **Immunity:** "The Hespori is currently immune to your attacks." printed at tick 72, while buds were alive.
- **Swing timing:** every swing is 6 ticks after the previous one (all 20 gaps), and the death follows the last swing at tick 126.
- **Ranged swing (anim 8224):** two projectiles 1639, one tick apart (t+1, t+2). Both hits land together at t+2. Fourteen ranged swings.
- **Magic swing (anim 8223):** one projectile 1640 at t+3, one hit at t+4. Seven magic swings.
- **Split:** 14 ranged to 7 magic out of 21 swings.
- **Entangle:** anim 8223 at tick 87. Projectile 1642 and the message at tick 91 (t+4). The first swing was at tick 3.
- **Entangle struggle:** five "You feel the vines loosen slightly as you try to move." lines (ticks 94 to 98), then "You manage to break free of the vines!" at tick 99 (the sixth click).
- **Kill:** Hespori death at tick 125, death animation 8225 at tick 126, "Your Hespori kill count is: N.", then "Fight duration: 1:17. Personal best: M:SS."
- **Poison:** "You have been poisoned!" at tick 11.

## Changed in the code

- `BUD_TILES` moved to the capture's four tiles (instance-relative through the same path as before).
- A killed bud leaves an 8585 flower on its tile (no combat, no drops). The flowers go when the next phase opens, or when the fight ends.
- Hit delays: spores 2 ticks, wave and vines 4. Swings are picked at the swing and land through the special's per-kind `hitDelay` and `anim`. Death animation 8225.
- Swing split: 2 in 3 ranged (one kill, so the odds are weak).
- Messages: "The Hespori entangles you in some vines!", "You manage to break free of the vines!", "The Hespori is currently immune to your attacks.".
- Kill: "Fight duration: M:SS. Personal best: M:SS." (personal best kept as the player's var `hespori.best`, in ticks).

## Left as it was

- 300 hit points, the 66%/33% thresholds, 8 per spore (2 prayed), 14 per wave (3 prayed), poison.
- Entangle gap (30 to 40 seconds). Weak evidence it may be longer: the capture had one entangle, at tick 87, and none in the remaining 39 ticks.
- Fight size: no group scaling.

## Guessed or not verified

- Split: one kill's worth of swings.
- Flowers are not attackable: relies on the cache's 8585 having no "Attack" action (not checked in the cache).
- Fight duration: counted from the awaken tick to the kill tick (122 ticks here, against the capture's 1:17 = about 128). The capture's start point is unknown.
- Bud tiles reachable by melee: not checked. The capture's player attacked with ranged.
- Projectiles 1639, 1640, 1642 and the poison gfx 1641 are not played (no projectile calls in the special path). Still deferred (`DEFERRED(other)`).
