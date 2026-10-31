package io.github.fleton1.bosscapture;

import net.runelite.client.config.Config;
import net.runelite.client.config.ConfigGroup;
import net.runelite.client.config.ConfigItem;
import net.runelite.client.config.Range;

@ConfigGroup(BossCaptureConfig.GROUP)
public interface BossCaptureConfig extends Config
{
	String GROUP = "bosscapture";

	@ConfigItem(
		keyName = "bossNames",
		name = "Boss names",
		description = "Comma-separated NPC names. A capture starts when one of these is nearby.",
		position = 0
	)
	default String bossNames()
	{
		return "Zulrah, Vorkath, Kraken, Cerberus, Abyssal Sire, Alchemical Hydra, Grotesque Guardians, Dusk, Dawn,"
			+ " Kalphite Queen, King Black Dragon, Giant Mole, Sarachnis, Scorpia, Callisto, Artio, Venenatis, Spindel,"
			+ " Vet'ion, Calvar'ion, Chaos Elemental, Commander Zilyana, General Graardor, Kree'arra, K'ril Tsutsaroth,"
			+ " Nex, Corporeal Beast, Dagannoth Rex, Dagannoth Prime, Dagannoth Supreme, Phantom Muspah, The Nightmare,"
			+ " Phosani's Nightmare, Duke Sucellus, The Leviathan, The Whisperer, Vardorvis, Scurrius, Amoxliatl,"
			+ " The Hueycoatl, Araxxor, Crystalline Hunllef, Corrupted Hunllef, TzTok-Jad, TzKal-Zuk, Sol Heredit,"
			+ " Tempoross, Zalcano, Wintertodt, Gemstone Crab, Obor, Bryophyta, Hespori, Skotizo, Royal Titans,"
			+ " Branda the Fire Queen, Eldric the Ice King, Yama, Doom of Mokhaiotl, Brutus,"
			+ " Blood Moon, Blue Moon, Eclipse Moon";
	}

	@ConfigItem(
		keyName = "recordAlways",
		name = "Record everything",
		description = "Record a session right now, with or without a boss nearby. Turn off to end it.",
		position = 1
	)
	default boolean recordAlways()
	{
		return false;
	}

	@Range(min = 5, max = 500)
	@ConfigItem(
		keyName = "endAfterTicks",
		name = "End after (ticks)",
		description = "End the capture once no boss has been nearby for this many ticks.",
		position = 2
	)
	default int endAfterTicks()
	{
		return 50;
	}

	@Range(min = 8, max = 64)
	@ConfigItem(
		keyName = "radius",
		name = "Radius (tiles)",
		description = "NPCs and objects within this many tiles of you are recorded.",
		position = 3
	)
	default int radius()
	{
		return 32;
	}

	@ConfigItem(
		keyName = "outputDir",
		name = "Output folder",
		description = "Where JSONL captures are written. Blank means ~/osrs-captures.",
		position = 4
	)
	default String outputDir()
	{
		return "";
	}
}
