# Barrows brothers against the captures (2026-10-30)

Branch `boss/barrows-captures`. Source: `data/captures/barrows/*.jsonl.gz` (Ahrim, 283 ticks, all five brothers; Dharok,
73 ticks, tunnels only), read with `tools/barrows/bar.py` and `bar2.py`. Wiki: `tools/wiki/mirror.py page`. Captures
beat the wiki; the wiki's max hits are the ones used.

## Attacks

| Brother | Swing anim | Gap (capture) | Hit delay (capture) | Gap, code now | Delay, code now | Wiki speed |
|---|---|---|---|---|---|---|
| Ahrim | 1167 (1163 once) | 6 | +1 (at distance 1) | 6 (was 7) | 1 (was 3) | 6 |
| Karil | 2075 | 4 | +1 (at distance 2) | 4 (was 7) | 1 (was 2) | 4 |
| Guthan | 2080 | 5 | 0 | 5 | 0 | 5 |
| Torag | 2068 | 5 | 0, two hits a swing | 5 | 0, one hit | 5 |
| Verac | 2062 | 5 | 0 | 5 | 0 | 5 |
| Dharok | 2067 | one swing only | 0 | 7 (was 7) | 0 | 7 |

Gaps count block animations (2079, 424, 430, 2063) as nothing; the swing gap follows the swing anim. Ahrim's 1163 swing
at tick 9 took its own six-tick slot. Dharok's 7 is the wiki's; the capture has one swing.

Max hits (wiki infobox, all 100 hitpoints): Ahrim 20, Karil 20, Guthan 24, Torag 23, Verac 23, Dharok 29 (57 at 1 hp).
They were already the code's.

Distance: the capture's Ahrim swung at distance 1 and Karil at 2, both with a +1 delay. Only those distances were seen,
so a flat delay of 1 is built for both. OSRS's distance-scaled delay for magic and ranged is not checked here.

## Set effects

| Brother | Effect (wiki) | Built | Prayer |
|---|---|---|---|
| Ahrim | 20% a hit: Strength -5 | yes | works under Protect from Magic (wiki) |
| Karil | 25% a hit: Agility -20% | yes | works under Protect from Missiles (wiki) |
| Torag | 25% a hit: run energy -20% of current | yes | works under Protect from Melee (wiki) |
| Guthan | 25% a hit: heal for the damage | yes | stopped by Protect from Melee (wiki) |
| Verac | Defiler, 25% a swing: ignores defence and armour, penetrates protection prayers | yes | max hit 15 under Protect from Melee (wiki infobox) |
| Dharok | Wretched Strength: +1% max hit per hitpoint missing | yes (`dharokMaxHit`) | none |

The effects run on a successful hit, before prayers, through a new `Content.onNpcHitRolled` hook. Torag's two hammers
hit twice a swing through `NpcAttackStyle.hits`. Verac's Defiler rolls its hit against defence 0
(`NpcAttackStyle.ignoresDefence`).

Guessed: the Defiler's 15 under Protect from Melee is the wiki's infobox reading, not a capture sample. The Strength and
Agility drains restore as the engine's other drains do. Karil's "regardless if the hit would have been successful" is
read as: the 25% is rolled on each hit that rolls successfully, and PfM does not stop it.

Not built: Ahrim's Confuse, Weaken and Curse. The capture has one such swing in seven (1163 at tick 9, "You feel
confused.", no hitsplat after it). The wiki gives no odds and the attack's mapping from anim to spell is unknown, so
they are left out under `DEFERRED(barrows-spells)`.

## Messages

| Event | Capture (order) | Code now |
|---|---|---|
| Dig into a crypt (box) | "You've broken into a crypt!" on the dig tick, the teleport on the next | same (added) |
| Search a sarcophagus and raise him | "You don't find anything." then the brother's overhead "You dare disturb my rest!", same tick (4 of 4 after the first) | same (added) |
| Search one already handled | not in the capture | "You have already searched in this sarcophagus." (2006 text, kept) |

The brief expected "You don't find anything." for an already-handled tomb. The capture shows it on each raising search,
so it is used there. The already-handled text has no capture sample, so 2006's line is kept. The overhead is set with
`Npc.say`; the content tests cannot read it back, so it is checked by reading the code only.

## Tunnels

The Dharok capture has crypt rats (1679, 1680, 1681), crypt spiders (1683, 1684), skeletons (1685-1688) and Riyl Shadow
(1281) on plane 0 around x 3514-3574, y 9693-9717. `spawns_world_fill.json` had six of these tiles (on plane 0, as the
brief expected). The other capture spawn tiles were added in `data/spawns241/spawns_barrows_tunnels.json` (33 rows,
src `capture`; rows within two tiles of an existing world-fill row of the same id are dropped, as WorldSpawnsTest requires). Riyl Shadow had none before; it has two now. Their level and names match
the cache: the capture's combat levels equal the cache's.

The Ahrim, Karil, Guthan, Torag and Verac tunnels are on plane 3. The Dharok capture's tunnel is on plane 0. Its tomb
(20720) in the cache is on plane 3 at (3554,9714), so this capture does not settle which floor Dharok's tunnel is on.
The Dharok tomb and its stair are not changed.

## Dig landings (capture path, teleport ticks)

| Dig box (code's DIG_AREAS) | Capture landing | Code | Result |
|---|---|---|---|
| Dharok (3570-3579, 3293-3302) | (3556,9718,3) | (3556,9718,3) | exact |
| Guthan (3571-3582, 3278-3285) | (3534,9704,3) | (3534,9704,3) | exact |
| Karil (3562-3569, 3273-3279) | (3546,9684,3) | (3546,9684,3) | exact |
| Torag (3550-3557, 3278-3287) | (3568,9683,3) | (3568,9683,3) | exact |
| Verac (3553-3561, 3294-3301) | (3578,9706,3) | (3578,9706,3) | exact |
| Ahrim (3561-3568, 3285-3292) | not seen | (3557,9703,3) | kept |

The brief's (3556,9701,3) was the first sample of the recording, already in the tunnel, not a dig landing, so the code's
(3557,9703,3) is kept.

Climb-ups (not dig landings, reported only): Ahrim's arrives at (3565,3290) against the code's (3565,3288); Torag's at
(3552,3282) against (3554,3282); Dharok's at (3572,3295) against (3574,3297). Each is two tiles off, so these three were
not changed; Guthan's (3578,3283) and Karil's (3567,3274) are within a step.

## Not covered

- Chest and rewards: no capture (the Ahrim capture stops 50 ticks after a brother, and the chest was not reached).
- Ahrim's stat-lowering spells (above).
- Dharok's fight beyond one swing: the 7-tick gap is the wiki's.
