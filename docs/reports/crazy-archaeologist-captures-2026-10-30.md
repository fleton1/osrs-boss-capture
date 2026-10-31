# Crazy archaeologist (Bellock): the 2026-10-30 capture

Source: `data/captures/crazy-archaeologist/crazy-archaeologist-20261030-182559.jsonl.gz`, one fight of four kills
(deaths at ticks 92, 188, 290, 407). Figures from `tools/crazy-archaeologist/stats.py` (run with `python3 -I` on a
gunzipped copy). The captures beat the wiki; these numbers replace the placeholders in `CrazyArchaeologist.kt`.

## Findings

**Swings.** The capture has 100 ranged projectiles (`1259`, two ticks after each ranged swing), 3 melee swings
(anim 423) and 13 specials. The brief's 90 counted only the `3353`/`423` animations: on 10 ranged swings the player's
block animation (`425`, every 4 ticks while he is hit) overwrote the `3353` on the same tick. So 116 swing slots in all.
Swing gap: 3 ticks in 61 of 89 gaps; 6-tick gaps come from specials and from a few missed slots.

**Special ("Rain of knowledge!").** Tick `t` is the say.
- Books leave at `t+2` (projectile `1260`, 79 cycles); all three explode at `t+4` (gfx 157 on each tile).
- The first book's two splits leave at `t+4` (120 to 122 cycles) and explode at `t+8`.
- A player between two books took both (8 and 5 at tick 117). The 3x3 holds.
- Protection prayers don't stop the books.
- Specials take a swing slot: the rain's swing has no ranged projectile and no hit (checked over all 13 rains).

**Aim.** The first book goes to the player's tile at the swing. Over 13 specials: the swing tile matched in 12 (both
tiles in 10, the swing tile only in 2); the tile one tick later matched in 1 (rain 212, the brief's example). So the
brief's "about t+1" is one case of thirteen, and the code's pick-time aim stays. A player who steps off after the
throw takes nothing (rain 7: the player walked away on the melee tick; rain 49, 311 likewise).

**Scatter.** Books 2 and 3 land within Chebyshev 4 of the first (26 books: distance 1 ten times, 2 ten, 3 four, 4 two).
Splits likewise: 1 eight, 2 thirteen, 3 two, 4 three. `SCATTER` is 4. This is the measured maximum of 26 samples;
the distribution may be wider than seen.

**Cadence.** Gaps between specials: 42, 33, 31, 34, 27, 38, 33, 30, 36, 27, 27, 27. Every gap is at least 27
(the 25-tick cooldown, rounded up to the swing grid). Nine of the twelve are on the 3-tick grid; the other three (31,
34, 38) follow pauses in his swings, which shift the grid. The 1-in-3 roll per swing fits the cadence.

**Ranged hit delay.** From the swing, first hitsplat (a 0 counts), by distance:

| distance | delay 1 | delay 2 |
|---|---|---|
| 2 | 5 | 2 |
| 3 | 2 | 11 |
| 4 | 4 | 25 |
| 5 | 2 | 41 |
| 6 | 0 | 6 |
| 7 | 0 | 2 |

Melee (3 swings, anim 423): delay 0, on the swing tick.

**Overheads.** One line on every swing except the special: 100 of 100 ranged swings, 3 of 3 melee. The six lines
are roughly equal (22, 21, 20, 15, 14, 11 over 103). "Ow!" on each of the four deaths, one tick after the death.
Specials say "Rain of knowledge!" (13).

**Respawn.** 14 ticks from the hide (despawn) in all three respawns (hide 95, 191, 293; back 109, 205, 307).

**Animations and projectiles.** Ranged swing anim 3353, death 836, block 425. Projectile 1259 for the ranged attack,
its flight 5 x (distance + 1) cycles (15 at 2 tiles, 40 at 7). Books `1260`, 79 cycles; splits 120 to 122.

## What the code had right

- 225 hit points, the 14 max hit, the 3-tick swing, reach (ranged out to 8, melee beside him).
- Spawn (2977,3702); no pet; the 3x3 explosion; the 25-tick cooldown and 1-in-3 roll.
- Melee on the swing tick (delay 0 is the engine's default for melee).
- Protection prayers don't stop the books.

## What changed, and what is not done

- Specials: books leave at `t+2`, explode at `t+4`; splits leave at `t+4`, explode at `t+8` (was: explosion at `t+1`,
  split at `t+3`).
- `SCATTER` 2 to 4. `BOOK_MAX` stays 24 (the capture only shows rolls of 1 to 11).
- Ranged hit delay: 2 for every distance. The engine's style has one fixed delay for ranged swings (Combat.kt only
  takes a per-swing delay for melee), so distance 2 lands a tick late (the capture: 1 tick at 2 tiles). A per-distance
  delay is not worth an engine change now: `DEFERRED(combat)` in `CrazyArchaeologist.kt`.
- Ranged projectile 1259 and the books' 1260 are sent. The engine's own flight time is used for the ranged one
  (not 5 x (distance + 1)); the books use 79 and the splits 120 cycles.
- Ground graphic 157 for the explosions: not done (`DEFERRED(render)`). The engine has no call to show a ground graphic.
- Melee animation 423: not done (`DEFERRED(render)`). The engine has one attack animation per NPC (3353).
- Lines and "Ow!": done. The overhead text is the engine's; the tests read it through `CrazyArchaeologist.said`.
- Respawn: 14 for Bellock (6618) only; the Chaos Fanatic (6619) keeps 15.
