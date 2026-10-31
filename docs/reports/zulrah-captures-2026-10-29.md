# Zulrah from real OSRS captures (2026-10-29)

The capturing player recorded Zulrah kills on live OSRS (rev 241) with the log-only RuneLite plugin
in this repo. These recordings replace
the Near-Reality fan-server tables that `Zulrah.kt` used before. The player had judged those tables wrong, and they were.

- **Data:** `data/captures/zulrah/*.jsonl.gz`: 13 files, about 20 kills, all four rotations, several of each. The
  plugin README describes the format: one JSON object per line, real-world tiles, and NPC/object tiles as the centre of
  the footprint.
- **Tools** (`tools/zulrah/`, Python, read `.gz` directly):
  - `phases.py <dir>`: each fight as its phases. Form+spot (G/R/B, M/E/W/S) and its actions: `r`/`m` orbs, `t` tail,
    `Cx,y+x,y` a barrage's two cloud middles (first-landing first), `Ex,y` an egg's tile.
  - `consensus.py <dir>`: the phases lined up by rotation, with how often each version was seen.
  - `timing.py <dir>`: gaps between Zulrah's animations, and the projectile flights.

## Rotations (consensus; every repeat agreed on the tiles and the order)

Clouds are the middles of their 3x3 clouds; within a pair, the first one listed lands first.

| Rot.ph | Stand | Actions |
|---|---|---|
| all .1 | green middle | C 2269,3069+2272,3069 · C 2263,3070+2266,3069 · C 2273,3072+2273,3075 · C 2263,3076+2263,3073 |
| 1.2, 1.5, 1.10 / 2.2, 2.6, 2.10 | red middle | tail ×2 |
| 1.3 / 2.3 | blue middle | 4 mixed |
| 1.4 | green south | r5 · E 2263,3076 · E 2263,3073 · C 2263,3070+2266,3069 · C 2272,3069+2273,3072 · E 2273,3075 · E 2273,3078 |
| 1.6 | blue west | 5 mixed |
| 1.7 | green south | C 2269,3069+2272,3069 · C 2263,3070+2266,3069 · C 2263,3073+2263,3076 · E 2272,3069 · E 2273,3075 · E 2273,3078 · E 2273,3072 |
| 1.8 / 2.8 | blue south | 5 mixed · E 2263,3070 · C 2266,3069+2269,3069 · E 2263,3076 · C 2272,3069+2273,3072 · E 2263,3073 |
| 1.9 / 2.9 | green west (Jad) | r m r m r m r m r m · C 2263,3070+2266,3069 · C 2269,3069+2272,3069 · C 2263,3073+2263,3076 · C 2273,3072+2273,3075 |
| 2.4 | green west | C 2273,3072+2272,3069 · C 2273,3075+2273,3078 · C 2269,3069+2266,3069 · E 2266,3069 · E 2263,3070 · E 2263,3073 · E 2263,3076 |
| 2.5 | blue south | 5 mixed · then as 1.4's eggs and clouds |
| 2.7 | green east | r5 |
| 3.2 | green east | r5 · E 2273,3078 · E 2273,3075 · E 2273,3072 |
| 3.3 | red middle | C 2273,3078+2273,3075 · E 2273,3072 · C 2272,3069+2269,3069 · E 2266,3069 · C 2263,3073+2263,3070 · E 2263,3076 · tail ×2 |
| 3.4 / 3.6 | blue west / east | 5 mixed |
| 3.5 | green south | r5 |
| 3.7 | green middle | C 2273,3075+2273,3078 · C 2272,3069+2273,3072 · C 2269,3069+2266,3069 · E 2263,3070 · E 2263,3076 · E 2263,3073 |
| 3.8 | green west | r5 |
| 3.9 | blue middle | 4 mixed · C 2263,3073+2263,3076 · C 2266,3069+2263,3070 · E 2269,3069 · E 2272,3069 · E 2273,3072 |
| 3.10 | green east (Jad) | m r m r m r m r m r |
| 3.11 | blue middle | E 2263,3076 · E 2263,3070 · E 2273,3072 · E 2273,3078 |
| 4.2 | blue east | E 2272,3069 · E 2273,3078 · E 2273,3075 · E 2273,3072 · 6 mixed |
| 4.3 | green south | r4 · C 2263,3070+2269,3069 · C 2266,3069+2272,3069 |
| 4.4 | blue west | E 2263,3076 · E 2263,3073 · E 2266,3069 · E 2269,3069 · 4 mixed |
| 4.5 | red middle | tail ×2 · then 4.3's two pairs |
| 4.6 | green east | r4 |
| 4.7 | green south | E 2263,3076 · E 2263,3073 · E 2263,3070 · E 2273,3072 · E 2273,3075 · E 2273,3078 · C 2273,3075+2273,3078 · C 2272,3069+2273,3072 · C 2269,3069+2266,3069 |
| 4.8 | blue west | 5 mixed · E 2263,3076 · E 2263,3073 · E 2263,3070 · E 2266,3069 |
| 4.9 | green middle | r5 (seen once) |
| 4.10 | blue middle | 4 mixed · C 2263,3073+2266,3069 · C 2263,3070+2263,3076 · C 2269,3069+2272,3069 |
| 4.11 | green east (Jad) | m r m r m r m r |
| 4.12 | blue middle | E 2263,3076 · E 2263,3073 · E 2273,3075 · E 2273,3078 |
| last | green middle | r5 · the opening's four pairs (the next rotation's phase 1) |

The optional extra green stand never showed up in about 20 kills. Snakeling type (2045 melee or 2046 magic) looks
random per egg.

## Spots (Zulrah's centre tile)

Middle (2268,3075), east (2278,3073), west (2258,3073), south (2268,3064). Our east and west spots were each one tile
off; they are fixed.

## Timings

- Dive (5072) to emerge (5073): 3 ticks. Emerge to first action: **3** (we had 2).
- Actions every 3 ticks. Zulrah holds **one extra tick** before it sinks after a barrage or egg. It also holds one
  before switching to something else after **3 or more** barrages or eggs in a row (C×3 → E, E×4 → orb, E×6 → C).
  Shorter mixed runs (E E C C E E, C E C E) stay at 3.
- Tail swings 8 ticks apart, and the dive comes 8-9 ticks after the second. A tail stand lasts 22 or 23 ticks.
- Projectiles leave 40 client cycles into the spit (a barrage's second 45). Flights are fixed: orbs 50 cycles,
  barrage orbs 50 and 75, eggs 80. So an orb's hit lands on tick 3, a barrage's clouds on ticks 3 and 4, and an egg on
  tick 4, whatever the distance. A cloud object appears as its orb ends and lasts about 29 ticks.
- Rotation 1's stand lengths now match the captures (ZulrahTest): 22, 18, 40, 22, 21, 29, 37, 49, 22.

## Still open

- ~~Hidden behind a pillar~~ built (user confirmed: "hiding behind pillar does that"). While the player is out of
  sight at a strike's turn Zulrah waits; after 6 ticks it drops the stand's run of strikes and goes on to its orbs and
  barrages. Captured: 2.5 hidden from the start threw no strikes, its first orb 6 ticks after the first strike's turn;
  a 4-tick hide in 1.8 only delayed the next strike. Bot batch after it: 18/20 (seeds 3 and 20 die early).
- Animation 5808 plays right before most dives and some spits (a look or turn?); not modelled.
- Checked 2026-10-30: all 13 captured fights start with the rise (5071) and their first spit 11 ticks later, and their first
  sink 24 ticks after the rise. Later rises are emerges (5073), 3 ticks to the spit, as `EMERGE_TICKS`. Engine: `RISE_TO_ACTION`
  = 11; tests `the first attack comes eleven ticks...` and `the opening stand ends 24 ticks after the rise...`.
- Projectile cosmetics (start height 172, end 124 on the player, slope 16) are not applied.

## Bot check

`ZulrahBotFight` (render241, slow), batch of 20 at commit 8cfb408c (2026-10-30): 19 kills, 1 death, seed 18 (rotation 2,
blue phase, 226 damage, 7 sharks; three ranged orbs in a row hit it while it prayed against magic). The seed-3 death
quoted before this pass no longer happens: seed 3 is a kill at 364 s. Seeds 1-60 at the same commit: 59 kills, 1 death
(seed 18), so seed 18 is a roll the bot can lose, not a timing regression.
The bot's own copy of the spot tiles was updated too; with the old east/west tiles it could not spot the Jad phase.
