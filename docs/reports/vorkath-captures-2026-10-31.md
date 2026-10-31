# Vorkath: captures against the remake, 2026-10-31

**Sources:** `data/captures/vorkath/vorkath-20261031-140852.jsonl.gz` (kill 57, 4:27, "fight A") and
`vorkath-20261031-141353.jsonl.gz` (kill 58, 3:58, "fight B"). Measured by `tools/vorkath/measure.py`
(`python3 -I tools/vorkath/measure.py data/captures/vorkath/*.jsonl.gz`). Wiki: "Vorkath" and "Vorkath/Strategies" (mirror).
Ticks are the capture's `tick` field (0.6 s). Hit and projectile timings are as the client recorded them.

**Short version:** the attack order, the 5-tick grid, the six-standards rule and the alternation of the two specials all
match both fights. Four things did not match and are changed: the acid pool count (20 to 57), the acid's life (20 to 25
ticks), the deadly fireball's landing (3 to 5 ticks after the swing) and the spawn's distance (10 to 8 tiles). The spawn's
lead-in and the standards' hit delay do not match and are left open (below).

## 1. The claims, the code, the captures

Counts: "A" = fight A, "B" = fight B. "1 sample" marks a value seen in one fight only.

| Claim | Code (before) | Captures | Verdict |
|---|---|---|---|
| Wake-up: poke, first attack | poke wakes, attacks at once | poke tick 1, first swing tick 1 (A and B) | Matches |
| Swing speed | 5 ticks | Non-melee standards: 45 of 46 gaps = 5 (A), 44 of 45 = 5 (B); the other gap is 3 | Matches |
| Standards before a special | 6 | Every block is exactly 6 non-melee standards: 8 of 8 blocks (A), 7 of 7 (B) | Matches |
| Alternation, first special random | alternates; first random | A opens with Rapid Fire, B with the spawn; then strict alternation in both | Matches |
| Melee swing (anim 7948) | standard melee in reach | 10 (A) and 22 (B) swings off the 5-tick grid; none has a hitsplat of its own | Open (see 4) |
| Rapid Fire: swing to pools | pools at the swing (lead 1 via hit delay) | pools 3 ticks after the swing: 7 of 7 phases | **Changed** (lead 3) |
| Pool count | 20 | **57** in each of 7 of 7 phases (both fights) | **Changed** (57) |
| Acid life | 20 ticks | **25** ticks from landing (pools gone at +25), 7 of 7 | **Changed** (25) |
| Barrage | one shot a tick on the player's tile while the pools last | a shot each tick from landing+1 to the last tick of the acid | Matches the shape |
| Acid burn and heal | 1-10 burn, Vorkath heals the same | burns 7 to 10 seen; heal equal to burn (10 to 10, 9 to 9, 7 to 7) | Matches (1 sample of exact heal per type) |
| Standing-still barrage damage | 25-41 | one hit seen: **24** (fight A), below 25 | One sample, open |
| Next standard after Rapid Fire | (phase end + timer) | next standard at swing + 33 in 7 of 7 phases (acid end + 5) | Open (engine timer, see 4) |
| Spawn: breath, freeze | breath = the special's swing, freeze at once | the swing is an attack anim (7952) with projectile 395; the breath anim (7960 + 1484) is 3 ticks later and the freeze message is on that tick, 8 of 8 | **Changed** (freeze lands 3 ticks after the swing) |
| Spawn appearance | with the breath | 7 ticks after the swing: 4 ticks after the freeze, 8 of 8 | **Changed** (4 ticks after the freeze, scheduled) |
| Spawn landing distance | 10 tiles | **8** tiles (Chebyshev) from the frozen player, 8 of 8 | **Changed** (8) |
| Spawn walk | 1 tile a tick | distance falls by 1 a tick (8, 8, 7, 6, ...) | Matches |
| Spawn life | ends on burst or death | burst after 8 ticks (A), killed after 12, 9, 10, 9 ticks | Matches |
| Spawn burst damage | up to 60 scaled to its hit points | 55 once (A, first spawn); the spawn's hit points at the time are not known | One sample |
| Freeze and immunity | frozen until the spawn ends; immune while it lives | freeze ends on the burst or the death; "immune" messages during the phase | Matches |
| Freeze message | "frozen in place" | "You have been frozen!" | **Changed** (text) |
| Deadly fireball | launched at the player's tile; lands 2 ticks later; a tile away half | lands at swing + 5 (flight 4 ticks after a tick's start), 19 of 19; the player walked off and took nothing in the 9 cases in which they moved | **Changed** (5) |
| Dragonfires (standard, venom, corrupt) | hit at the code's delay | every standard hit lands 3 ticks after its swing: magic 17 of 17, ranged 24 of 24, fire 18 of 18, venom 8 of 8, corrupt 8 of 8 | Open (see 4) |
| Venom and prayer loss | venom; prayers off | "You have been poisoned by venom!"; "Your prayers have been disabled!" | Matches (wording differs, see 4) |
| Kill and loot | kill count, head at 50, loot on one of 8 tiles | death at 444 (A) and 396 (B); kill count message 7 ticks later in both; loot lines on the same tick as the message | Matches (timing of the message is not modelled) |
| Sleeper after the kill | back to sleep with no timer | sleeper 8059 on the kill's tick; in A it became 8058 44 ticks later | Matches (8058 change not modelled) |

## 2. What changed, and the evidence

- **`ACID_POOLS` 20 to 57.** Seven of seven rapid phases in the two fights placed 57 pools. Source: the captured object spawns
  and burst projectiles (1483).
- **`RAPID_TICKS` 20 to 25.** The acid lasts 25 ticks from its landing in all seven phases (landing and removal are object
  events in the capture).
- **Rapid Fire lands 3 ticks after its swing** (`kindDelay`). The capture shows the pools 3 ticks after the swing in seven of
  seven phases. Note: the same 3 is the captured delay of the standard dragonfires; the code's standards land after 1 tick
  (see 4), so 3 here is the captured number, not the code's own convention.
- **The deadly fireball lands 5 ticks after its swing, on the tile the player stood on when it was swung.** The old code
  landed after 3 ticks (hit delay 1 plus a 2-tick timer). The capture's flight starts 1 tick after the swing and ends 4 ticks
  later.
- **The spawn's breath lands 3 ticks after its swing** (was 1, the registered delay). Freeze message wording changed to the
  game's line.
- **`SPAWN_DISTANCE` 10 to 8.** Eight of eight spawns (both fights) were 8 tiles from the player at first sight. The wiki
  says ten ("always lands ten tiles away"); the captures decide.
- **Spawn appearance: 4 ticks after the freeze.** The summon is scheduled (`SPAWN_APPEARS`), and the phase waits for it
  (`spawnTick` used to end the phase while no spawn was out: that was the reason the earlier attempt never summoned).
  The spawn does not walk on the tick it comes out.

## 3. Test changes

- New pins in `VorkathTest`: the rapid fire's 57 pools and 25 ticks; the deadly's 5-tick landing; the spawn's 3-tick
  landing and 8-tile distance.
- Two existing tests (`deadly dragonfire ... half a tile away`, `... two tiles off`) now move the player before the
  fireball lands, and set the launch tile first. Their assertion values are unchanged. The reason: the fireball now
  evaluates the player's tile when it lands, as the capture's flight does.
- One test renamed from "ten tiles off" to "eight tiles off" (its range 6..10 is unchanged).
- No existing assertion value changed.
- Spawn timing: the tests that read the spawn after the breath wait `SPAWN_APPEARS + 1` calls (the freeze shows on the first
  tick call after `beginSpawn`, which runs between ticks). Pinned by behaviour, not only constants: the rapid and breath
  landings are measured through the fight's own swing loop (`swingToLanding`), and the breath's freeze line is checked.
  The old eight-tile test accepted 6 to 10, so it passed with 10; it now asserts 8. Each changed value was reverted once in a
  batch run (`tools/suite.sh content '*Vorkath*'`): every reverted value failed its own test.

## 4. Open (not changed)

1. **Standard hit delay.** Every standard hit lands 3 ticks after the swing in both fights (59 samples). The code's
   magic and ranged styles use hit delay 1, and a standard dragonfire is a special kind in the engine (`kind != 0`), so the
   `+2` for dragonfire does not apply: it lands after 1 tick too. This is the engine's hit-delay convention for NPC styles
   (`Combat.kt`, the swing's delay), a shared engine rule. Not changed.
2. **Spawn appearance: fixed** (see section 3). Not verified on a device; the test world shows it 4 ticks after the freeze.
3. **Post-special resumption.** After Rapid Fire the next standard is at swing + 33; after the spawn it is 0-1 ticks after
   the freeze ends. The code keeps a fixed 5-tick timer, so the gap cannot be reproduced without a per-special timer. Engine
   item.
4. **Melee (anim 7948).** 10 and 22 off-grid swings, with no hitsplat of their own. Whether they strike, and when, cannot be
   told from these captures (other hits land on the same ticks). Not modelled; the grid is clean without them.
5. **Barrage hit rule.** One hit (24 damage) was seen across about 200 barrage shots; seven shots where the player stood on
   the aimed tile for two ticks drew no hit. The capture's tile readings may lag a tick. The wiki's "stand still and
   take 25-41" was not confirmed. Not changed.
6. **Acid-phase damage.** Vorkath took a 100-damage hit (A) and a 43 (B) during the acid. The 50% reduction cannot be
   checked from hitsplats alone (raw damage unknown). Not changed.
7. **Wording.** The captured lines "The spawn violently explodes, unfreezing you as it does so.", "You become unfrozen as
   you kill the spawn.", "Your prayers have been disabled!", "You have been poisoned by venom!" and "The dragon is currently
   immune to your attacks." differ from the code's. The code's burst line is pinned by existing tests, so it stays.
8. **Spawn burst damage.** One sample (55). The formula (remaining hit points scaled to 60) is consistent with partial
   damage, but the spawn's hit points are not captured.
9. **Kill-to-message timing and the 8058 change.** Not modelled.

## 5. Single-sample values

- 24 (barrage damage, below the wiki's 25), 55 (spawn burst), 100 and 43 (hits during the acid, raw damage unknown).
- The 4-tick spawn appearance is 8 of 8, not a single sample, but the fix did not land.

## 6. Found in review (98e8bd6f re-check, not yet explained)

- In the test world the acid pool objects were gone from `w.objects` about 22 ticks into a 25-tick phase, and the phase was
  still `RAPID` 1 to 2 ticks past `phaseUntil`. Not isolated (the rapid test now asserts only that the acid is still down at
  +24). Worth a look before the next Vorkath change: a phase that outlives its timer would keep the 50% reduction on.
- The standard hit delay (item 1) and the post-special resumption at swing+33 (item 3) are unchanged.

