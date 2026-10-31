# Moons of Peril captures, measured (2026-10-31)

Source: `data/captures/moons/` (rev 241): one fight each of Eclipse, Blue and Blood, plus a full run of all three. So there are
six fights, two per Moon. Ticks are 600 ms, counted in the capture. Numbers live in `content/MoonsOfPeril.kt` and
`quests/PerilousMoons.kt` (repeat form), pinned in `MoonsOfPerilTest`.

## Rhythm: agreed in all six fights

| What | Measured | How used |
|---|---|---|
| Swing gap | 6 ticks | `SWING_TICKS` 9, 15 ... 39 from the phase's first glyph |
| Swings per phase | 6 (2 per sigil, 3 sigils) | as above; the old code counted the same six |
| First swing after a phase's glyph | 9 ticks (Eclipse 74 to 83, Blood 56 to 65) | `SWING_TICKS[0]` |
| Hits after the swing animation | 1, 2, 3 ticks | `HIT_DELAYS` |
| A miss | all three splats are blocks (type 12) | `repeatSwing` |
| Glyph moves | 3 ticks after every 2nd swing | `SIGIL_MOVE_TICKS` 18, 30. Differs from the quest form, which moves on the player's attacks |
| Special start after the last swing | Eclipse 3, Blue and Blood 6 | `specialTick` |
| Kill to move out | last hit +1 Eyatlalli's tracker npc 13009, +7 more the move: 6 of 6 | `KILL_TO_MOVE` 8 |

## Specials: start to next glyph

| Moon | Special | Ticks | Samples | Follows |
|---|---|---|---|---|
| Eclipse | Searing Rays | 49 | 3 | east sigils |
| Eclipse | Clones | 54 | 4 | west sigils |
| Blue | Frost Storm | 53 | 2 | east sigils |
| Blue | Weapon Freeze | 49 | one sample | west sigils |
| Blood | Blood Rain | 22 | 3 | west sigils |
| Blood | Blood Jaguar | 44 | 2 | east sigils |

This order matches the wiki's new/full moon rule. Fights start on the east set here, which is a choice: the live fight runs
without the player, so a capture can't show its start.

## Geometry

- The Moon's cache size is 1, but the player melees from 3 tiles off its tile on every side, so the fight treats it as 5 x 5
  centred on the tile. The world spawn stays one tile; the repeat form swaps in a five-tile copy of the type for the fight.
- Threat circle npc 13015 from the centre: (2,4) (4,2) (4,-1), special, (-1,-3) (-3,-1) (-3,2), special. Moon sigils (2,-3) and
  (-1,4) appear only in the Jaguar.
- Safe tiles: the player's tile relative to the circle was (0,0) (-1,0) (0,-1) (-1,-1) in nearly all clean ticks, so a sigil is
  two tiles square with the circle's tile at its north-east. Off it: 1, 1, 2 seen, consistent with the wiki's doubling.
- Shield npc 13020: tick-by-tick path in `SHIELD_PATH`, one rotation (one sample of the path, repeated in timing by the others).
  Rays: anim 11018 / gfx 2784 from tick 10, every 3, 12 of them; projectile 2781 two ticks later; lands 3 after the anim.
- Ray rule: straight line from the centre to the player, blocked by the shield's 2 x 2. Checked against 22 rays of the full run:
  20 agree. Ray damage 9, 9, 5 (few samples, code rolls 5-9).
- Blood Jaguar: eight 13021 at the offsets in `JAGUARS`, marked one beside its sigil (2 samples of which); pools square radius
  3 every 6 ticks from tick 5, 24 tiles; jaguar swing every 6 from tick 8 (12491). Hits on the marked one gave back 1-3 HP.
- Blood Rain: 307 pools over ticks 4-21, life exactly 5 ticks (307 of 307), about 15 a tick. Moon gone ticks 7-23.
- Frost Storm: heals on ticks 7, 17, 27, 37, 47 of 10 per unlit brazier (seen 20, 10, 0, 0, 0). Storm hits 7, 5, 8, 7: code rolls
  3-8. Storm npc 13027: up to 28 visible at once; the code keeps a dozen, because their walking is not modelled closely.
- Weapon Freeze: block npcs 13025 at (-5,-1) (4,-3) (2,6), six punches of 11 then the cracked 13026 with one of 6: 72 hit points
  and a fixed 11 (one sample). Lines: "Your weapon freezes over. You're forced to let go!", "You retrieve your weapon from within
  the cracked ice."
- Clones: npc id 13012, not the cache's named clone 13019 (the quest form keeps 13019). Three at +0, +2, +4 of each cycle; five
  cycles 9 ticks apart from tick 10; swing +3 (11022), hit +4. Unparried blow: 9 (one sample).
- Moths: 15 to 37 to 59 prayer, so 22 a catch (2 of 2), matches the wiki. Moth npc 12772, tiles from the capture, one sample.

## Post-kill move

Eclipse first: (1376,9710) Earthbound. Blue after Eclipse: (1351,9582) Ancient. Blood after Blue: (1351,9582) Ancient. All match the
wiki's rule, used as `campAfter`. **Streambound's tile is a guess** beside its stove, as no capture ended there.

## Chosen, not measured

- Entry: the statue sets the player on the first east sigil. Captures land on whatever the running fight's sigil is ((-4,-2) Blue,
  (0,0) Blood), which this fight, starting on entry, has no equivalent of.
- `RAY_CURSE` 20 and `BRAZIER_WARMTH` 9: the wiki says only "large" and "a portion". Shards 3-6: "light damage". Weapon Freeze failure
  rolls 1-28 from the wiki's "up to 28". Glance takes 12 off the hit, where the wiki takes it off the max hit.

## Measured, not built

- Hitsplat type 44 on the player about four ticks before each move (147-172): HP doesn't change, so it isn't a heal. Not used.
- The Moons' self-damage: the player dealt 460 and 496 on Blue, 915-939 with heals on Blood, 207-346 on Eclipse (both Eclipse
  captures started mid-fight). No formula can be read off these; left out (DEFERRED), which makes the fight a little longer.
- The Blood Moon's special edge wall (51054, 60 tiles): scenery only.
