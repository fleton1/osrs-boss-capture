# Giant Mole against the 2026-10-30 capture

Source: `data/captures/giant-mole/giant-mole-20261030-175605.jsonl.gz` (revision 241, world 356): three kills and a partial,
94 swings. Analysis scripts: `tools/giant-mole/` (run with `python3 -I` on the gunzipped file). NPC positions in the
capture are centre tiles; the mole is size 3, so its engine tile (SW corner) is one less in x and y. Captures beat the
OSRS wiki, and the wiki beats everything else. No fan-server tables are used.

## What the capture shows, and what the engine now does

| Fact | Capture | Engine |
|---|---|---|
| Hit points | 200 (one full kill's hits sum to 201) | 200, kept |
| Swing gap | 4 ticks (87 of 94 gaps) | `attackTicks` 4 from the definition, kept |
| Hit delay | 0: the hit is on the swing's tick | `npcAttackStyle(hitDelay = 0)` |
| Animations | attack 3312, block 3311, death 3310 | `npcAnims` with those ids |
| Respawn | 16 ticks from despawn, twice (a third, 27, probably out of view); despawn 3-4 ticks after death | 16 for 5779 (`Combat.respawnTicks`) |
| Respawn tile | centre 1760,5190 all three times | SW 1759,5189 in `data/spawns241/spawns_giant_lairs.json`; the 2006 row at 1760,5189 is dropped in `data/remap/rev241_drops.txt` |
| Comes back | full hp | kept |
| Burrow odds | 6 burrows in about 32 attacks in the 50%..5% band | one in four, kept (wiki: 25%) |
| Burrow sequence | t: anim 3314, gfx 572 on the centre (571 on the outer eight); t+1: four projectiles 570; t+2: anim 3315, at the destination, gfx 573 there | t: anim 3314, gfx 572 on her, the stop of her pending hits; t+1: four projectiles 570; t+2: anim 3315 and the move; then frozen 3 ticks |
| Burrow distance | 11 to 27 tiles from her (five seen) | 11..27 from her; 3..27 from the player |
| Heals on burrow | no | no |
| Entry | dig at the hill at 2984,3387 (the capture recorded 2983,3387) landed the player at 1752,5237; rope 12230 stands at 1752,5136 | landing 1752,5237 for every hill |
| Dig message | "You seem to have dropped down into a network of mole tunnels." | added |
| Damage | 7 hits in 94 swings, max 19, high-defence gear | max hit 21 kept (not enough data to change it) |

## Not matched, or not built

- **Hills 2 to 6 (DEFERRED mole-lair).** The cache has six hills in Falador Park: 2984,3387, 2989,3378, 2996,3377,
  2987,3387, 2999,3375, 3005,3376. Only the one at 2984,3387 has a capture. The others use the same landing; the
  wiki's Giant Mole page gives no per-hill landing.
- **Payment.** The capture shows "Payment has been taken from your coffer: 6,250 Coins." just before the drop. Nothing
  explains it; it is not charged in the engine.
- **Ground graphics (DEFERRED render).** The capture plays graphic 571 on the eight outer footprint tiles and 573 where
  she comes up. The engine has no ground-tile graphic call, so only her own graphic 572 is played.
- **Light source (DEFERRED light).** The wiki says candles, torches and lamps go out when she is in melee range, and a
  Fire of Eternal Light stays lit. The capture shows no light source, so nothing is built or tested for it.
- **Unexplained burrow at tick 128.** Her burrow there (from 1739,5222, hp 14%) went out of view at tick 130 and came
  back at tick 149 at 1768,5174, 48 tiles from her old tile. It is outside the 11 to 27 range, so it is not in the
  five destinations above, and the engine rule keeps 11 to 27. Whether it is a real long burrow or a far walk the recorder
  missed is not known.
- **Further out-of-view moves (not in the table, review 2026-10-30).** The capture also loses her from view with her
  alive at ticks 379 (last seen 1778,5165) and 411 (last seen 1772,5174) of the third kill, and she is seen again at 380 at
  1776,5167. The recorder cannot say whether these are burrows or walks out of its view; the 379 to 380 gap is only 2 tiles,
  so it is probably a walk. The 1739,5222 to 1768,5174 move at tick 128 to 149 is the 48-tile case above.
- **Capture's first mole (tick 0, 1739,5231).** It is not in the spawn data (the data has one mole, at the respawn tile).
  It is the capture's first kill, before the player arrived; not used.
- **Attack animations and the 3-tick stand.** The stand is a frozen-tick count, so she does not swing while stood.
  Animation ids are set; the tests do not read them (the engine keeps them internal).

## Tests

`content/src/test/kotlin/oldkingdom/content/GiantMoleTest.kt`: hill entry and landing, rope, four-tick
cadence, burrow decision to arrival (two ticks) and the three-tick stand, burrow distance and walkable footprint over six
seeds, the player keeps the target and walks after the burrow, no burrow above 50% or below 5%, loot, and respawn (16
ticks from despawn, at the SW spawn, full health).
