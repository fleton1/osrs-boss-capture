# Sarachnis from real OSRS captures (2026-10-29)

The capturing player recorded 4 Sarachnis kills (8713) on live OSRS (rev 241, world 356, instanced: false) with the log-only RuneLite
plugin. Data: `data/captures/sarachnis/sarachnis-20261029-193735.jsonl.gz` (ticks 0-756, 4 kills, has an `end` line).
Readers (`tools/sarachnis/`, read the `.gz`, run with `python3 -I`): `timeline.py <file> <from> <to>` (her and her spawns'
anims, projectiles, splats on the player, her tile and HP ratio); `stats.py <file>` (kills, HP, heals, gaps, projectiles,
hit delays, prayers, webs, spawn thresholds).

Attribution: her spawns are 8714 (melee, size 2) and 8715 (ranged, size 2); she is 8713 (size 5). Each swing is attributed
to the NPC by id and by tile (nearest footprint centre within 2 tiles). Her tile in the tick data is her centre.

## Numbers

**Kills and respawn.** Spawns at ticks 47, 229, 427, 573; deaths at 204, 402, 548, 699. Respawn is **25 ticks** after
each of the 3 deaths (ours is 17). Her death takes both spawns with her.

**HP.** 400 checks out. Damage taken per kill (types 16, 43) minus heals is 406, 408, 406, 406. The last hit overshoots the
remaining HP by 6 to 8 each time, so the total is 400 with a last-hit overkill. The health bar's scale is 80 units (5 HP
each).

**Heals (hitsplat type 6), 7 in total, 5 or 10 each.** Six were 5, one was 10. Every heal came in the same tick or the tick
after a damaging melee hit of hers (8147) of 10 or more (6 of 6: 10, 10, 15, 19, 21, 21). Hits of 3 and 7 did not heal.
No heal after any of the 74 unprayed zero swings (blocked or missed), and no heal after a ranged hit (no damaging ranged
hit was seen). The "Sarachnis leeches some health as she damages you" message came with 4 of the 7 heals. The 10 is
unexplained (one heal; the other 5 melee-hit heals were 5). "It heals some health" is the player's karambwan, not her.

**Melee anim 8147 (boss).** Used when she is next to the player: 70 of 70 swings had the player 3 tiles from her centre (the
edge of her 5x5 footprint). Every splat lands on the anim tick (delay 0). Attack speed **4** (44 of 44 gaps after a melee
swing are 4). Unprayed: about 10 damaging hits and 74 zero splats (the windows also hold a few other swings' splats); max hit seen **23** (21, 21, 19, 15, 10, ...). Protect from Melee blocked 12
(zeros). Under Protect from Missiles only, a melee hit did land (21, 15, 19, 21): the prayers match the styles.

**Ranged anim 4410 (boss).** Used at 2 to 10 tiles (mostly 3 to 6; 28 of 69 at 3). Two projectiles follow it, 1686
(long flight, 27 to 127 cycles) and 1687 (short, 12 to 32 cycles), both starting 2 ticks after the anim. The splat comes
at anim + 4 (3 to 5). Of 23 projectile hits on the player, 21 were zeros (no prayer; 2 landed, max 21 on one, 11 on
the other). Speed: 4 or 6 ticks between ranged swings (17 and 23 gaps).

**Hit delays, summary.** Melee (boss and melee spawn): 0 (on the swing tick). Boss ranged: 4 (3 to 5). Spawn ranged: 3
(2 to 4; swing at +2 for the projectile, then 0 to 2 more).

**Webs and the bind ("Hsss!" overhead, 28 times).** Every fifth swing is the web: four standard swings (melee or ranged)
then the shout, 20 to 23 ticks apart (median 21; 27 of 28 cycles are 20 to 23). "Sarachnis has webbed you in place!" comes
2 ticks after each shout, and again about 4 to 7 ticks after it in 17 of the 28 cycles (43 messages in all, which we
cannot explain). "I can't reach that!" (49 times) is the player clicking while bound. Her movement: after a shout she
walks 3 to 4 tiles within 4 ticks and about 7 tiles within 8 ticks (her swings continue in between). The spotanim 1683
on the player came 22 times near the shouts (it is not tied to one attack, so we do not claim it is the web's graphic).

**Spawn thresholds.** Each line summons one pair: one 8714 and one 8715, on both lines, in all 4 kills. Boss HP just
before the spawn tick: first line 290, 280, 304, 270 (72.5%, 70%, 76%, 67.5%); second line 136, 148, 144, 146 (34%, 37%,
36%, 36.5%). The 70% and 37% lines fit these (the HP is read from the damage sum, so it is good to about 4 HP).

**Spawn sides.** The melee spawn 8714 was on her west side in 7 of 8 pairs, 4 to 11 tiles from her centre (median 7). The
ranged spawn 8715 was east (+1 to +5 tiles) in 4 of 8 pairs and level with her (-2 to 0) in the other 4.

**Melee spawn 8714.** Anim 8147 with no projectile: splats at delay 0. Attack speed **3** (123 of 136 gaps after a swing
are 3; the rest 4 or 6, when it walks). Unprayed max hit 13 (11, 13, 8, 7); Protect from Melee blocks it (zeros).

**Ranged spawn 8715.** Anim 4410 with projectile **1682** at anim + 2 (102 of 115 swings), hit at projectile + 0 to 3
(mode 1). Attack speed **4** (107 of 107 per-instance gaps). Unprayed max hit 21 (one of 13 landed hits; 82 of 95
projectiles were zero). Under the wrong prayer one hit did 7 (the data's prayer list at that tick).

**Projectiles.** 1682 belongs to the ranged spawn 8715 (98 of the 115 by tile; 16 by tile to the melee spawn and 1 to her, which
tile matching can misattribute when the spawns stand together). 1686 and 1687 are her ranged projectiles (4410). 85 is the impact graphic on the player (86 times); 1683
is the web graphic at the shouts (22).

**Heal check against the code.** The heal is on the player's damaging hits only (see above), not on zero hits.

**Max hits, prayers.** Her melee: 23 unprayed, 0 under Protect from Melee (12 blocked), 21 under Missiles only (no effect
on melee). Her ranged: 21 unprayed (one hit). Melee spawn: 13 unprayed. Ranged spawn: 21 unprayed (one hit).

## What the captures cannot tell

- The web's bind length (the wiki says 6 ticks; the captures only show the "webbed" lines and 22 "I can't reach" runs).
- Why "webbed" comes twice in about half the cycles, and what 1683 marks.
- The ranged heal (10 in our code): no damaging ranged hit landed on a heal-tick, so the amount and the rule are open.
- Why the one heal is 10 (the other six are 5).
- Whether 1686 and 1687 are two attack styles or one style with two graphics (both come from 4410, both are "ranged").
- The spawns' placement rule (both sides in the captures; no fixed rule beyond the melee spawn's west side).
- Ranged damage under Protect from Missiles: no ranged hit landed under that prayer on a non-zero swing.
- Her max hit (31, the wiki's): 23 is the highest seen; the captures do not refute 31.
- The private instance, the arena's floor, and the spawns' HP (the 30 hit points of the wiki, which the captures do not measure).

## Gaps against our code (Sarachnis.kt)

1. Respawn 17 -> **25**.
2. Spawn lines 66% and 33% -> **70% and 37%**.
3. The magic spawn (8715) is a **ranged** spawn with projectile 1682 (not magic, no projectile).
4. Melee spawn (8714) attack speed **3**; ranged spawn **4**. Our code has the default for the melee spawn.
5. Boss melee hit delay **0** (code 2); boss ranged hit delay **4** (code 2); spawn ranged **3** (code magic 3).
6. Heals only on a landed hit that does damage (code heals on any landed swing, zeros included; the wiki's "including
   zeros" is contradicted by 74 zero swings with no heal).
7. Web cadence every 5th swing (4 standard, then the web): ours is the same.
8. Her web moves her 3 to 7 tiles (ours 2 to 4 at once).
9. Her max hit 31 (kept; captures do not refute it).
10. Boss attack speed 4 (kept; ours is 4).

Left out (client): her 1686/1687 projectile graphics, the 1683 web graphic, and the impact graphics (the client is out of scope).
