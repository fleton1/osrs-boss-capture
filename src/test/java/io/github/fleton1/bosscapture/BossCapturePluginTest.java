package io.github.fleton1.bosscapture;

import net.runelite.client.RuneLite;
import net.runelite.client.externalplugins.ExternalPluginManager;

public class BossCapturePluginTest
{
	public static void main(String[] args) throws Exception
	{
		ExternalPluginManager.loadBuiltin(BossCapturePlugin.class);
		RuneLite.main(args);
	}
}
