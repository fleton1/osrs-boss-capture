# Alchemical Hydra from real OSRS captures (2026-10-29)

The capturing player recorded 7 Alchemical Hydra kills on live OSRS (rev 241, world 356) with the log-only
RuneLite plugin. The kills are fast and use one route: the Hydra is lured onto the vents the same way each time, and
the player always stands at the same tiles. Where something below was seen in only one place (the fire walls), the
tiles are exact and the general rule is a guess. That is said at each such place.

- **Data:** `data/captures/hydra/alchemical-hydra-20261029-163224.jsonl.gz` (ticks 0-2225, 7 kills; the file has an
  `end` line). NPC and object tiles are footprint centres (the 6x6 Hydra's centre is its SW tile + 3).
- **Tools** (`tools/hydra/`, Python, read `.gz` directly):
  - `timeline.py <file> <from> <to> | sort -n -s -k1,1`: one tick window, raw.
  - `attacks.py <file>`: each kill as its actions, one row a form (tokens explained in the header), then the
    totals per form and animation, the gaps between animations, and the damage on the player.
  - `fight.py <file> [kill]`: a kill as one line per Hydra animation, with the gap and the HP ratio at the form changes.
  - `specials.py <file> [poison|lightning|fire]`: each special's blobs, currents or walls, relative to the player.
  - `prayer.py <file>`: each 1662/1663 projectile, the protection prayer on when it landed, and its hit.

## Projectiles, styles and prayer

`prayer.py` settles the styles. **1662 is magic, 1663 is ranged**, the reverse of the first reading. Protect from Magic
stopped all 172 of the 1662 hits (all zero splats), and Protect from Missiles stopped all 132 of the 1663 hits. Every
damaging basic hit came with the other prayer up, or with no prayer. The prayer blocks fully, so the code's rule
holds. Every projectile is its own hit: one attack with two projectiles gives two hitsplats.

| Form | Magic anim (1662) | Ranged anim (1663) | Projectiles per attack | Highest hit seen unprayed |
|---|---|---|---|---|
| serpentine 8615 | 8236 | 8235 | 2 magic, 2 ranged | 12 / 14 |
| electric 8619 | 8243 | 8242 | **2 magic, 1 ranged** | 13 / 32 |
| fire 8620 | 8250 | 8249 | 1, 1 | 26 / 28 |
| extinguished 8621 | 8255 | 8256 | 1, 1 | 38 / - |

The code had one hit per attack and the forms' `attackAnim`. It now uses this table.

## The action clock (all 7 kills agree)

- Basic attacks are 6 ticks apart (4 in the last form). Lightning and poison take one 6-tick slot.
- **The style changes every 3 attacks, and the count runs on through the form changes.** The code reset it with each
  phase. Kill 1: the serpentine's last three magic attacks, then the transition's attack is ranged and is the first of
  three ranged attacks. A switch animation (9111 serpentine, 9112 electric, 9113 fire) plays 3 ticks after each third
  attack, which is 3 ticks before the next action. Specials do not count as attacks, and the count runs on across them.
- Each phase's special comes after its first 3 attacks, then after every 9 (as coded). Kill 2's last form: P, 9
  attacks, P.
- Specials seen per phase: poison 1-2 (7 kills: 2,1,1,1,1,1,1, kill 1 had 2), lightning 1-2, fire exactly 1 (the
  fire phase is short), enraged poison 1-2.
- The last form opens with the style opposite the fire phase's last attack (7/7) and alternates every attack, the
  special included in the alternation's count (M R M [P] R M ...). This matches the code.
- The first style of a kill: magic in kills 1, 2, 3 and 7, ranged in 4, 5 and 6. It is random, as coded.

## Form changes

| Change | Anims | Forms | Ticks to the next form | Next action after the new form |
|---|---|---|---|---|
| 75% | 8237 → 8238 | 8615 → 8616 → 8619 | 3 | +6 |
| 50% | 8244 → 8245 | 8619 → 8617 → 8620 | 2 | +6 |
| 25% | 8251 → 8252 | 8620 → 8618 → 8621 | 3 (once 2) | +4 |

- The HP ratio (of 120) at each change is 90 → 87-90, 61-62 → 58-60, 31-32 → 27-30. So the thresholds are 75%, 50%
  and 25%, as coded.
- When the change comes on an attack tick, the first anim (8237/8244/8251) carries that attack. It is the old form's
  attack (8616 threw 2, 8617 threw the electric counts, 8618 threw 1), and it counts toward the style but not toward
  the new phase's three before the special.
- Hitting the Hydra between the two forms gives "You cannot attack the Alchemical Hydra as it changes form!"
- The only chat at a change is "The Alchemical Hydra becomes enraged!" at 8621. The code's "roars as one of its heads
  falls away" and "loses its last head" lines were invented and are gone.
- "Roaaaaaaaaaaar!" is the Hydra's overhead text (16 times, once per right vent and phase), not a game message.

## Poison (8234; the last form's poison is anim 8256 with 1644)

- The anim tick is t. The 1644 blobs leave at t+1 (t+2 once), one at **the player's tile** and the rest at room tiles
  up to 7 away on an axis (relative tiles seen: -2,-5 · -3,-3 · -1,-2 · +2,-1 · +3,+1 · -3,-6 · -5,+6 · -5,+7 · 0,+7 ...).
  Blobs per poison: serpentine 5,5,5,5,4,4,3 (14 poisons over 7 kills), last form 1 ×6 and 5 ×2 (both of kill 2's).
- Flight is about 30 + 10 × the distance from the Hydra in cycles (50 at 2, 80 at 5, 100 at 7). The landing marker
  1645 shows at t. A splash (1646/1647/1650/1651/1652) plays at landing, and a pool (1654/1655/1658/1659/1660) plays a
  tick later. That is t+3 for the player's tile in the serpentine phase and t+2 in the last form.
- Damage shows as poison splats (type 65) with "You have been poisoned!": 5 when a blob landed on the player (kill 1,
  kill 2), 7 in the last form (kill 5), and 7 when the player stepped into a 15-tick-old pool (kill 2, tick 625). There
  were no ordinary damage splats. Standing on a pool's centre the tick after (kill 2, 626-630, the pool 16+ ticks old)
  and 24 ticks after (kills 3 and 5) did nothing. **A pool lasts 16 ticks** (seen: hurts at 15, gone at 16).
- Code before: 5 blobs within 4, landing 2 ticks on, a splat for 1-7 typed damage, pools for 30 ticks hitting 1-12 a
  tick, and its own "spits poison" message.

## Lightning (8241)

- At t+1 a 1664 orb flies to the room centre (1367,10267), where it stays as a graphics object. At t+4, t+5, t+6 and
  t+7, one 1665 current at a time leaves the centre for a start tile. **There is one current per quadrant**, in random
  order: x in 1360-1362 or 1371-1373, y in 10261-10263 or 10272-10274 (24 of 24 starts).
- Each current (graphics object 1666) then moves **one tile a tick toward the player's current tile**, diagonals
  included, for 12 tiles. When it reaches the player it ends with "The electricity temporarily paralyzes you!" (in
  red) and a hit of 15, 19, 23, 25 or 26 (5 seen; prayer does not matter). The code's maximum of 22 was too low; it is
  now 26, the highest seen. The paralysis held the player 5 ticks (kill 3; in the other cases the player stood still
  anyway).
- Code before: four marks at the room corners and one hit on the player's old tile 4 ticks later.

## Fire (8248 ×3)

- The special's slot comes 6 ticks after the third attack. **The Hydra walks** to the centre (SW 1364,10265, centre
  1367,10268), one tile a tick (7 ticks from its lure spot in every kill), and stays there to the end of the kill. It
  never moved again in 7 kills. On the tick it arrives, its 6x6 becomes 36 objects 26209 (SW 1364,10265 to 1369,10270),
  and the player gets "The Alchemical Hydra temporarily stuns you." 56 ticks later the 26209s give way to 29733s on
  the same tiles. Those stay until the next kill's flame, through the death and the respawn at the same centre.
- With the arrival at a, the anims come at t = a+2, a+5 and a+8, and the next attack comes 12 ticks after the third
  anim:
  - t: a wall of 32 fire graphics objects (1668), 4 wide (the footprint's middle four columns, x 1365-1368) and 8 long
    (y 10271-10278: from the footprint to the room's north edge), on the player's side. Four 1667 projectiles go to
    its first row.
  - t+3: the same on the other side the player is on (x 1356-1363, y 10266-10269: west), with four 1667s to its last
    column.
  - t+6: one 1667 to the footprint's corner by the player (1363,10271). A fire (1668) shows there and on the player's
    tile, then follows the player one tile a tick, for up to 15 tiles (kill 2). In the other kills the player stepped
    aside and the trail stopped after its first two tiles.
- The player always stood at 1364,10271 (north-west, against the footprint's north edge). Only the north + west case
  was seen, so the other three cases are mirrored by guess. The player was held 10 ticks from the stun message in all 4
  kills where it was measured. No fire damage was taken, so the fires' damage and burn stay the code's.
- Code before: a teleport to the centre, a 3-tick stun, two 5x5 fire blocks beside the player, a tracking fire from
  the centre after 3 ticks, no solid footprint, and the Hydra chasing again afterwards.

## Respawn and death

The `death` event is followed by the 8622 death form (3-4 ticks later) and the despawn 10 ticks after the death. The
new 8615 spawns 42 ticks after the despawn, 52-53 ticks after the death. Combat.kt has 43 ticks from the death, which is
core code; this is left for the orchestrator (see below).

## What changed in AlchemicalHydra.kt

- Anims, projectile counts and one hit per projectile per form and style; the switch anims.
- The style count runs on through phase changes.
- The two-step form change: the intermediate forms, the anims, immunity with the captured message, the 9-tick (6 after
  the new form) pause. The invented change messages are gone and "becomes enraged!" is added.
- Poison: the captured blob count and range, a flight-based landing, poison-coloured damage, and 16-tick pools.
- Lightning: the centre orb, four homing currents, one per quadrant, a hit up to 26 with a 5-tick paralysis, and the
  captured message.
- Fire: the walk to the centre, the 10-tick stun with the captured message, the solid 26209 footprint, the two 4-wide
  walls to the room's edge, a tracking fire from the footprint corner, and the Hydra staying at the centre.
- The solid footprint is taken away at the kill: our Hydra walks again after its respawn, and 29733 is solid here.
- Not changed (core): the 43-tick respawn in Combat.kt should be 52 from the death; this is a DEFERRED line. Also the
  engine's "You have been poisoned." (full stop; OSRS has "!").
