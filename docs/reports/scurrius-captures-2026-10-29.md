# Scurrius from real OSRS captures (2026-10-29)

The capturing player recorded 9 Scurrius kills on live OSRS (rev 241, world 356) with the log-only RuneLite plugin.
They were fought in the **private room**: the NPC is **7222** (`rat_boss_instance`, combat 200). Our `Scurrius.kt`
builds only the public room's 7221 (`rat_boss_normal`, combat 250, 1500 hp). 7221 shows once at tick 0, outside.

- **Data:** `data/captures/scurrius/scurrius-20261029-191826.jsonl.gz` (ticks 0-1372, 9 kills, has an `end` line).
  NPC tiles are footprint centres (3x3: SW + 1).
- **Tools** (`tools/scurrius/`, read `.gz`): `timeline.py <file> <from> <to>` (his anims, projectiles, hits on the
  player, heals, debris, rats, with his tile and HP ratio); `stats.py <file>` (per-kill damage and heals, attack gaps,
  hit delays with the prayers on, each stomp's debris).
- Anims: 10686 spawn, 10693 tail (melee), 10694 ranged, 10696 magic, 10698 stomp (debris), 10705 death, 10706 enrage;
  feeding forms 10695 ranged, 10697 magic, 10699 stomp, 10703 summon. Spotanims: 2638 magic cast, 2639 feeding magic
  cast, 2640 magic projectile, 2641 magic impact, 2642 ranged projectile, 2643 ranged impact, 2644 falling debris.

## Numbers

- **Hit points 500** (the private room). Damage dealt per kill minus his heals is 500-506 each time; HP bar scale 120.
- **Spawn:** anim 10686 at centre (3302,9868), **35 ticks after the death** (8 times). Our `RESPAWN` is 30.
- **Attack speed 4** outside feeding: every tail, stomp, magic and ranged is followed 4 ticks later (91 of 102 gaps;
  the rest are him walking).
- **Tail (melee):** the hitsplat is on the anim tick. Protect from Melee blocks it. Highest hits unprayed 20-21.
- **Magic / ranged:** projectile 2640 / 2642, 90 client cycles in flight; the hit lands **4 ticks after the anim**.
  The matching prayer blocked all of them (no damage under the right prayer).
- **Feeding:** he goes to a food pile twice a kill. The first time at 56-78% (most kills 67-78%), the second time at
  31-52%. While feeding he only uses the feeding anims (ranged, magic, stomp, summon), **5-7 ticks apart** (7 most often,
  then 5). He heals **5 or 10** per heal, 5-7 ticks apart, 5 to 9 heals per kill, each just before a feeding swing.
- **Rats:** always **6** per wave. They come from the feeding summon (10703, rats 2 ticks later) and on each
  **enrage** (10706, 6 rats 2 ticks later). Enrage happened at 0-18% HP in 6 of the 9 kills.
- **Debris (stomp):** 8-12 tiles a stomp (12 most often), graphic 2644 starting **60 cycles (3 ticks)** after the anim.
  The player's own tile is in the set 37 of 44 times (a shadow always falls on the player). The player reports: the
  shadows show, there is a moment, and a player standing in a shadow when the stone hits takes damage. In the
  captures the player stays on the shadow through +4 or +5 and is off it by +6 in 36 of 41 stomps, so the stones land
  at about +5/+6 (client ticks lag the server's by about one). The two clear hits (17 at tick 32, 16 at 134) both
  show at +5. Four stomps (491, 827, 1073, 1189) have the player recorded on a shadow at +6 with no hit, which the
  rule above does not explain yet. Stomps cut by his death (585) drop nothing. Next capture: stand still in one
  shadow for a stomp.

## Gaps against our code (Scurrius.kt)

1. Private room (7222, 500 hp) not built; our fight is the public 7221 at 1500 hp.
2. Respawn 30 -> 35.
3. Attack speed 4 (and 5-7 while feeding) is not modelled per phase.
4. Feeding at 80% and 30% with heals 4 ticks apart -> the captures: heals 5-7 apart, second feed nearer 50%.
5. Rat waves are 6, from the feeding summon and from the enrage under about 20% (not "12 waves in phase three").
6. Debris: 1 + 3 random pieces in our code; the captures have about 12 tiles around the room.
