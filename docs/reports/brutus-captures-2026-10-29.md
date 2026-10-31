# Brutus from real OSRS captures (2026-10-29)

The capturing player recorded Brutus (15626, the cow boss) on live OSRS (rev 241, world 356) with the log-only
RuneLite plugin, in the real Lumbridge cow field (`instanced: false`; other cows stay around). Most kills are a few
hits long. Three long fights were played on purpose. In kill 287 the player stood still and dodged both specials. In
kill 294 the player stood east of him, against the fence, and took the slams. In kill 300 the player took a charge.

- **Data:** `data/captures/brutus/brutus-20261029-190538.jsonl.gz` (ticks 0-1162, 16 kills; the file has an `end` line). NPC tiles are footprint centres (3x3: SW tile + 1).
- **Tool:** `tools/brutus/events.py <file> [from-tick]`: Brutus's anims, overheads, slam tiles, hits on the player,
  with the player's tile, HP and his centre and orientation on that tick.
- The player wore no prayer. Every one of his melee hits was a 0 (hitsplat type 12), so melee damage is not measured.

## The cycle

- Melee 13783 every **5 ticks**; the hitsplat lands on the anim tick.
- The **first special comes after 2 basics** (every kill that lived that long). After that there are **4 basics
  between specials** (kills 287 and 300). The first special is either one (charge in 287, 289, 291, 300; slam in 294,
  297, 298). Our code uses 4 or 5 every time.
- The specials alternate (kill 287: charge 97, slam 125, charge 169; kill 300: charge 1027, slam 1055, charge 1099).
- **A blocked charge becomes a basic.** In kill 294 the player stood east against the fence. He only ever slammed,
  with **9 basics** between the slams. That fits 4 basics, a charge slot spent as a basic, then 4 more. Our code uses
  the slam instead, which would give 4 basics between slams.
- After a special, the next melee comes **8 ticks** after the special's (last) anim (charge 97 -> 105, 1027 -> 1035, 1099 -> 1107; slams
  141 -> 149, 550 -> 558, 619 -> 627, 688 -> 696).

## Slam ("*snorts*", anim 13785)

- Three slams, **8 ticks apart** (125/133/141, 534/542/550, 603/611/619, 672/680/688, 741 then the kill). Our code
  spaces them at the attack speed (5).
- Each one lands **4 ticks after its anim** (matches `SLAM_HIT_DELAY`). The tiles are fixed on the anim tick: the
  player who steps out within the 4 ticks is safe, and one who steps inside the shape is still hit (552 -> 554).
- At the landing: spotanim **3589** on Brutus, graphic **3588** on every tile it hits.
- Between slams he may step one tile (diagonally) toward the player.
- **Shape: from the 8-way direction from his centre to the player** (his orientation on the tick, e.g. 256 SW,
  1536 E, 1792 SE). Straight -> the **row of 3** beside that side (seen east 7 times, north once at 893, south once at 1059).
  Diagonal -> an **L of 5**: the corner tile and the two tiles beside it along each side (seen SW 4 times, SE twice).
  At 1063 the player stood under his footprint's SE corner and got the SE L. The SE one at 550 had the player
  at (3265,3288) beside his east side's bottom tile, which our rule (diagonal only when outside both edges) calls a
  straight row of 3. The 8-way direction gives the 5-tile SE L that the capture has.
- **Damage 17-19** (8 hits: 17, 17, 18, 18, 18, 19, 19, 19; player HP about 91). Our code rolls 0 to min(19, 70% HP).

## Charge ("*growls*", anim 13778)

- The direction is locked on the anim tick and is **cardinal**. At 97 the player was (-1, +2) from his centre and he
  ran north.
- He starts moving **5 ticks after the anim** and covers 4 or 5 tiles at 2 a tick (north twice: 3288 -> 3290 ->
  3293; west: 3253 -> 3251 -> 3249; south: 3289 -> 3287 -> 3285). Our code lands it 3 ticks after the anim.
- **The hit lands 4 ticks after the anim**, one tick before he moves (1099 anim, 1103 hit, 1104 first step). The
  player stood straight south, beside his footprint, and was run through. **Damage 19** (one hit; the slam's 17-19
  suggests the same range).
- No spotanim or graphic.

## Spawn, death, respawn

- Cowbell Ring: "You ring the bell... and hear something approaching." comes **12 ticks** before the spawn anim
  13790 (6 times). Our code uses `RING_TICKS = 13`.
- Natural respawn: the spawn anim comes **35 ticks after the despawn** (40 after the killing hit; 5 times). Our code
  uses `RESPAWN_TICKS = 36`.
- He spawns at centre (3262,3288). He says "Moo" one tick before his first attack (5 ticks after the spawn anim).
- Death: "m-moo..." overhead and anim 13784 the tick after the killing hit, then the despawn 5 ticks later.
- Messages: "Brutus enters. The cows scatter." (MESBOX). "Your Brutus kill count is: N." and "Fight duration: m:ss.
  Personal best: ..." (GAMEMESSAGE). "The amulet has N charges." after a Ring.

## Still to capture

Nothing needed for the build. More charge hits would firm up its damage range.
