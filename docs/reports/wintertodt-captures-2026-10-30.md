# Wintertodt against the captures, 2026-10-30

Captures: `data/captures/wintertodt/wintertodt-20261030-185746.jsonl.gz` (555 ticks, one round won at tick 54, then a
second round from tick 155 to 547) and `wintertodt-20261030-190428.jsonl.gz` (414 ticks, second capture added by the
coordinator). Analysis: `tools/wintertodt/stats.py` and `timing.py`, run with `python3 -I` on a gunzipped copy.
Energy, drain and round length are untouched (solo pace approved, solo-scaling-audit.md).

## Matches (no change)

- Respawn: 100 ticks after a win (captures: 101 between the win and "Light this brazier!").
- Cold damage: 6 each time at 97 Firemaking, matching `coldDamage` with 4 warm items and 3 lit braziers (floor(6 * 100 / 97) = 6).
- Snowfall warning: the 1311 corner gfx and 502 centre gfx appear 3 ticks before the fall (90 cycles in both bursts),
  so AREA_WARNING_TICKS = 3 stays. The 3x3 is centred on the player.
- Area attack and the player's 3x3 damage rule as coded.

## Changed

- **Cold cadence:** the standard attack now rolls every 5 ticks (COLD_CYCLE_TICKS), with a 10-tick cooldown (COLD_COOLDOWN).
  The roll divisor is 5, so solo rounds get about one cold per 50 ticks (measured below). The other attacks keep their
  50-tick rolls and the same odds as before (the capture does not give their rate).
- **Cold message:** "The cold of the Wintertodt seeps into your bones." on the roll tick; the hit lands the tick after
  (capture: chat 159, splat 160). The old "The cold bites into you." is gone.
- **Chop 3 ticks** (was 4). The capture used a dragon axe, but the wiki says a steel axe at 46 Woodcutting already gives
  maximum cut speed, so the axe is not the cause. The code has no axe tiers, so the interval is the same for any axe.
- **Fletch 4 ticks** (was 3), as the brief says.
- **Pyromancer strike:** 8 to 11 per hit (capture: 11, 8, 10, 8, 8 and 8, 8, 11). The same-value type 6 splat is one
  strike, not a heal, per the coordinator's second capture. Two hits still put her down (14 hp).
- **Pyromancer overheads:** "Yemalo shi cardito!" with anim 4432 on each bolt; "Light this brazier!" at round start and
  when a brazier goes out; "Fix this brazier!" when one shatters; "We can rest for a time." on a win.
- **Messages:** "The brazier has gone out." (was "A brazier goes out."); "You need a tinderbox or Bruma Torch to light
  that brazier."; "There's no need to do that at this time." on a brazier action between rounds; "You get a bruma root.";
  "You carefully fletch the root into a bundle of kindling."; "Your inventory is too full to hold any more roots." (no
  root is taken); "You have run out of bruma roots." after the last root is fed.
- **Win:** "You have gained N Firemaking XP." (N = level x 100), "Your subdued Wintertodt count is: N.", then "You're owed
  an additional N rewards from the reward cart. You're now owed M rewards." (replaces the old message).
- **Supply crate:** "You have helped enough to earn a supply crate." once, when the round's points first reach 500.

## Guessed or not matched

- **Supply crate threshold:** the capture only shows the message at tick 435. The wiki pages cached here do not give a
  number. 500 is a guess (the reward cart's minimum).
- **Win XP: settled.** The capturing player's Firemaking is 97 (the player reports), so the capture's 9700 is 97 x 100,
  matching level x 100 (the wiki). The 6 cold damage also fits floor(6 * 100 / 97).
- **Snowfall tile graphics** (1311 and 502) are not played: the engine has no tile graphic call. Only the NPC gfx on the
  pyromancer exists (Npc.graphic). Not added.
- **Pyromancer damage roll:** a uniform 8 to 11 is a guess from six hits (the wiki gives no number).
- **Cold rate:** the capture's rate is about 1 per 35 to 50 ticks (15 cold hits in about 790 active ticks, both captures).
  The earlier solo code averaged about 1 per 100 ticks (5 colds a round). The new roll gives about 1 per 58 (8.4 colds
  a round over 20 seeds, 20 of 20 won). That is roughly double the old solo cold count, so solo is somewhat harder than
  before. Checked against a bot, not confirmed in play.
- **NPC 7373** (the invisible helper) is not reproduced.
- **Not in the capture, kept:** "Heavy snow begins to fall around you!", "The snow falls on you.", "A brazier shatters!"
  and "A pyromancer falls!" are not in the capture's chat, but the capture may just not have had those events.

## Tests

`tools/suite.sh content '*Wintertodt*'`: 13 tests, 0 failed. New: the cold's cadence over 12 seeds at full energy (gaps
multiples of 5, at least 10, mean about 30) and the hit a tick after the message; chop and fletch intervals from the click
(4 and 5, the script's 3 and 4 plus the click's tick); the solo win's messages (XP, subdued count, rewards owed, the crate
mark, the cold message).
