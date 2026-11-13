# osrs-boss-capture

A RuneLite plugin that records boss fights to JSONL files, so the
offline boss scripts can be checked against real fights tick by tick. With **Record everything**
on, it records any activity the same way: skilling, Agility laps, minigames, Sailing.

> Not affiliated with or endorsed by Jagex or RuneLite. Old School RuneScape and everything it
> contains belong to Jagex. Use this at your own risk and within Jagex's rules.
>
> **Sharing data:** captures hold your display name, other players' names and your kill counts. Run
> `python3 tools/scrub.py IN OUT.jsonl.gz` before you publish a capture. Text it hasn't seen becomes
> `[unreviewed line]`: read what it prints, and add safe lines to `tools/known_lines.txt`.

It is **log-only**: no overlays, no sounds, no menu entries, no input. Nothing is shown
during a fight, so it stays clear of the banned boss-helper features in Jagex's
[Third Party Client Guidelines](https://oldschool.runescape.wiki/w/Update:Third_Party_Client_Guidelines)
(attack prediction, projectile markers, prayer indicators, attack counters, and so on).
Don't add any of those to it.

## What it records

One JSON object per line. Every line has `type`, `tick` (ticks since the capture
started) and `cycle` (client cycle, 20 ms). Coordinates are real-world tiles: instance
remapping is undone.

| type | contents |
| --- | --- |
| `session` | boss, start time, game revision, world, instanced |
| `tick` | your tile, animation, pose, HP, prayer points, run energy, target; active prayers (when they change); every NPC in range with id, tile, orientation, animation, pose, HP ratio, target; while you sail, your own boat (`boat`: sea tile with the sub-tile offset, heading and the heading it is turning to, its type and size, and your tile on the main map). Other players' boats are never recorded |
| `npc_spawn` / `npc_despawn` / `npc_change` | NPC index, id, name, size, combat level; form changes (e.g. Zulrah colours) |
| `anim` / `spotanim` | animation or spot-anim changes on you or an NPC in range |
| `projectile` | id, start and end cycle, slope, start and end height, source and target tile and actor |
| `graphics_object` | tile graphics (e.g. Vorkath fire), id, start cycle, height |
| `object_spawn` / `object_despawn` | game objects in range (clouds, pillars...) |
| `hitsplat` / `death` | on you or an NPC in range |
| `sound` / `area_sound` | sound id, delay, source, tile, range |
| `overhead_text` | NPC shouts |
| `chat` | game and dialogue messages only; other players' chat is never recorded |
| `equipment` | your worn item ids, at the start and when they change |
| `end` | why it ended, tick count |

Other players are left out of everything except as an anonymous `"player"` target.

## When it records

A capture starts when an NPC from the **Boss names** list is within **Radius** tiles of
you, and ends once none has been near for **End after** ticks (default 50, about 30 s),
or when you log out or hop. **Record everything** forces a capture with no boss (for
waves, minigames, or bosses missing from the list).

Files land in `~/osrs-captures/<boss>-<yyyyMMdd-HHmmss>.jsonl` unless **Output folder**
is set.

## How to use it

It isn't on the Plugin Hub, so it runs in a RuneLite developer client built from this
repo. You need a JDK 11+.

1. **Close the Bolt RuneLite** (log out first) so only one client is running.
2. **Start the capture client:**

   ```bash
   bin/capture-client
   ```

   It refuses to start while the Bolt RuneLite is open. The first run downloads
   RuneLite and takes a minute or two. Optional: `bin/install-shortcut` adds
   **RuneLite (Boss Capture)** to your app menu next to Bolt.
3. **Log in with your Jagex account** using the Jagex sign-in panel in the developer
   client. RuneLite's
   [Using Jagex Accounts](https://github.com/runelite/runelite/wiki/Using-Jagex-Accounts)
   guide has the steps. Don't use `--insecure-write-credentials`, and delete any old
   `~/.runelite/credentials.properties`.
4. **Check the plugin is on:** open the plugin panel (wrench icon), find **Boss Capture**
   and make sure it's enabled. Its settings (boss list, radius, end delay, output folder,
   Record everything) are in the same place.
5. **Go fight a boss normally.** Nothing appears on screen; recording starts when the
   boss is nearby. The client log (`~/.runelite/logs/client.log`) shows
   `boss capture started: <file>` and `boss capture ended`.
6. **Find your recording** in `~/osrs-captures/`, one file per fight, e.g.
   `zulrah-20261029-201500.jsonl`. Summarise it yourself
   (below), and run `tools/scrub.py` before you share it.

Tips:

- Boss missing from the list? Add its exact in-game name to **Boss names**, or turn on
  **Record everything** for the fight and off again afterwards.
- Long gaps between phases (e.g. a boss diving or a cutscene)? Raise **End after
  (ticks)** so one fight doesn't split into two files.
- The capture client keeps its own settings in `~/.runelite`, separate from Bolt's, so
  Hub plugins you want there have to be installed in it once.

## Going back to the normal client

Nothing in the Bolt client was changed: not its plugins, settings, or files. The capture
client is a separate program with its own settings folder, so switching back is just
closing one and opening the other.

```bash
bin/normal-client
```

This asks before closing the capture client (log out in game first), then opens the
Bolt launcher. Or close the capture window yourself and open Bolt from the app menu.

To remove the capture setup completely:

```bash
bin/uninstall
```

It closes the capture client, removes the app-menu shortcut, and asks before deleting
the capture client's `~/.runelite` folder. Your recordings in `~/osrs-captures` are kept.
The JDK in `~/.local/jdks` is only used by this; delete it if you like.

## Reading a capture

```bash
tools/summarize.py ~/osrs-captures/zulrah-20261029-201500.jsonl
tools/summarize.py ~/osrs-captures/zulrah-20261029-201500.jsonl --npc 2042
```

This prints NPC forms, animations with the common gaps between them (attack speed),
projectile flight times, spot anims, sounds and damage taken.

## Capture checklist

Updated automatically as recordings are added. The number is how many recordings each fight has.

<!-- checklist:start -->
**18 of 63 captured**, 99 recordings in all.

- [ ] Abyssal Sire
- [x] Alchemical Hydra (1)
- [ ] Amoxliatl
- [ ] Araxxor
- [ ] Artio
- [x] Barrows Brothers (2)
- [x] Blood Moon (1)
- [x] Blue Moon (1)
- [x] Branda the Fire Queen (1)
- [x] Brutus (1)
- [ ] Bryophyta
- [ ] Callisto
- [ ] Calvar'ion
- [ ] Cerberus
- [ ] Chaos Elemental
- [ ] Commander Zilyana
- [ ] Corporeal Beast
- [ ] Corrupted Hunllef
- [x] Crazy Archaeologist (1)
- [ ] Crystalline Hunllef
- [ ] Dagannoth Prime
- [ ] Dagannoth Rex
- [ ] Dagannoth Supreme
- [ ] Doom of Mokhaiotl
- [ ] Duke Sucellus
- [x] Eclipse Moon (1)
- [ ] Eldric the Ice King
- [x] Gemstone Crab (1)
- [ ] General Graardor
- [x] Giant Mole (1)
- [ ] Grotesque Guardians
- [x] Hespori (1)
- [ ] K'ril Tsutsaroth
- [ ] Kalphite Queen
- [ ] King Black Dragon
- [ ] Kraken
- [ ] Kree'arra
- [ ] Nex
- [ ] Obor
- [ ] Phantom Muspah
- [ ] Phosani's Nightmare
- [ ] Royal Titans
- [x] Sarachnis (1)
- [ ] Scorpia
- [x] Scurrius (2)
- [ ] Skotizo
- [ ] Sol Heredit
- [ ] Spindel
- [x] Tempoross (3)
- [ ] The Hueycoatl
- [ ] The Leviathan
- [ ] The Nightmare
- [ ] The Whisperer
- [ ] TzKal-Zuk
- [ ] TzTok-Jad
- [ ] Vardorvis
- [ ] Venenatis
- [ ] Vet'ion
- [x] Vorkath (2)
- [x] Wintertodt (2)
- [ ] Yama
- [x] Zalcano (3)
- [x] Zulrah (13)

Plus 61 longer recording(s) that span several fights.
<!-- checklist:end -->

### Beyond bosses

Kept by hand (the list above is bosses only). These are recorded with **Record everything** on; a minute or
two of each is plenty, and several can share one file. Ticked ones have at least one recording.

**Agility**
- [x] Every rooftop course (Draynor to Ardougne)
- [x] Gnome Stronghold, Barbarian Outpost, Wilderness, Werewolf, Ape Atoll, Penguin
- [x] Shayzien (Basic and Advanced), Colossal Wyrm (Basic and Advanced), Prifddinas
- [ ] A course with a fall on it (rope swing, log, ledge)

**Skilling**
- [x] Woodcutting, every tree up to redwoods
- [x] Mining, every ore up to runite
- [x] Fishing, every method; Cooking on a fire and a range
- [x] Firemaking (a line of fires)
- [x] Smithing (smelting and an anvil)
- [x] Hunter (box traps, chinchompas)
- [x] Thieving: a stall and a guard's arrest
- [ ] Thieving: pickpocketing until stunned
- [ ] Runecrafting (an altar trip)
- [ ] Fletching, Crafting, Herblore (a few of each)
- [ ] Cooking: a whole stack in one go, with a burn

**Minigames and activities**
- [x] Vale Totems, including a full ent round
- [x] Zalcano (solo and mass)
- [x] Pest Control (Veteran)
- [ ] Tempoross, Wintertodt or Guardians of the Rift (one round)
- [ ] Royal Titans: a fight where you loot one Titan

**Sailing**
- [x] Sailing between ports (wind, trimming, a hazard)
- [x] Port tasks: one delivered, one to the wrong port
- [x] Salvaging a shipwreck and sorting it
- [x] A castaway rescue
- [ ] Charting, trawling, a sea creature, Barracuda Trials

**Travel**
- [ ] Fairy ring, spirit tree, gnome glider, canoe, minecart, quetzal, a ship

**Out and about**
- [x] A walk round Lumbridge and Draynor (for NPC placement)
- [ ] The same for Varrock, Falador, Ardougne, Seers', Civitas, the Kourend houses

## What's in this repo

- `src/`, `bin/`: the plugin and its launcher scripts (`bin/` assumes Linux with the Bolt launcher).
- `data/captures/<boss>/`: scrubbed recordings of real fights (rev 241), gzipped.
- `docs/reports/`: what was measured from each boss's captures. They were written for a private offline
  project, so references to its source files (such as `Vorkath.kt`) won't resolve here. The measurements stand alone.
- `tools/`: `scrub.py`, `check_captures.py`, `summarize.py` and the Zulrah and Vorkath readers.

## Contributing

Recordings of unticked bosses are the most useful thing you can add: see [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

The code, including `tools/`, is BSD-2-Clause (see `LICENSE`). The captures in `data/` and the reports in `docs/` are
CC0 1.0 (see `LICENSE-DATA`): whatever rights this project holds in them are given up, so use them freely. That covers
only this project's own rights. Old School RuneScape's content, including the game text and ids they record, stays Jagex's.
