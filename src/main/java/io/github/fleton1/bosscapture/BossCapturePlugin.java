package io.github.fleton1.bosscapture;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.inject.Provides;
import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.EnumSet;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.stream.Collectors;
import javax.inject.Inject;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.Actor;
import net.runelite.api.ActorSpotAnim;
import net.runelite.api.ChatMessageType;
import net.runelite.api.Client;
import net.runelite.api.GameObject;
import net.runelite.api.GameState;
import net.runelite.api.GraphicsObject;
import net.runelite.api.Hitsplat;
import net.runelite.api.Item;
import net.runelite.api.ItemContainer;
import net.runelite.api.NPC;
import net.runelite.api.NPCComposition;
import net.runelite.api.Player;
import net.runelite.api.Prayer;
import net.runelite.api.Projectile;
import net.runelite.api.Skill;
import net.runelite.api.WorldView;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldPoint;
import net.runelite.api.gameval.InventoryID;
import net.runelite.api.events.ActorDeath;
import net.runelite.api.events.AnimationChanged;
import net.runelite.api.events.AreaSoundEffectPlayed;
import net.runelite.api.events.ChatMessage;
import net.runelite.api.events.GameObjectDespawned;
import net.runelite.api.events.GameObjectSpawned;
import net.runelite.api.events.GameStateChanged;
import net.runelite.api.events.GameTick;
import net.runelite.api.events.GraphicChanged;
import net.runelite.api.events.GraphicsObjectCreated;
import net.runelite.api.events.HitsplatApplied;
import net.runelite.api.events.InteractingChanged;
import net.runelite.api.events.ItemContainerChanged;
import net.runelite.api.events.NpcChanged;
import net.runelite.api.events.NpcDespawned;
import net.runelite.api.events.NpcSpawned;
import net.runelite.api.events.OverheadTextChanged;
import net.runelite.api.events.ProjectileMoved;
import net.runelite.api.events.SoundEffectPlayed;
import net.runelite.client.RuneLite;
import net.runelite.client.config.ConfigManager;
import net.runelite.client.eventbus.Subscribe;
import net.runelite.client.events.ConfigChanged;
import net.runelite.client.plugins.Plugin;
import net.runelite.client.plugins.PluginDescriptor;

/**
 * Passive boss-fight recorder. It writes what the client already received to a JSONL
 * file and never draws, plays, or sends anything: no overlays, no menu entries, no input.
 */
@Slf4j
@PluginDescriptor(
	name = "Boss Capture",
	description = "Logs boss fight data to JSONL files for analysis. No overlays.",
	tags = {"boss", "logger", "data", "export"}
)
public class BossCapturePlugin extends Plugin
{
	static final int FORMAT_VERSION = 1;

	private static final Set<ChatMessageType> CHAT_TYPES = EnumSet.of(
		ChatMessageType.GAMEMESSAGE,
		ChatMessageType.SPAM,
		ChatMessageType.ENGINE,
		ChatMessageType.MESBOX,
		ChatMessageType.DIALOG
	);

	private static final DateTimeFormatter FILE_STAMP =
		DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss").withZone(ZoneId.systemDefault());

	@Inject
	private Client client;

	@Inject
	private BossCaptureConfig config;

	@Inject
	private Gson gson;

	private Set<String> bossNames = Collections.emptySet();
	private CaptureWriter writer;
	private int sessionTick;
	private int ticksWithoutBoss;
	private List<String> lastPrayers;
	private final Set<Projectile> seenProjectiles = Collections.newSetFromMap(new IdentityHashMap<>());

	@Provides
	BossCaptureConfig provideConfig(ConfigManager configManager)
	{
		return configManager.getConfig(BossCaptureConfig.class);
	}

	@Override
	protected void startUp()
	{
		bossNames = parseNames(config.bossNames());
	}

	@Override
	protected void shutDown()
	{
		endSession("plugin stopped");
	}

	@Subscribe
	public void onConfigChanged(ConfigChanged e)
	{
		if (!BossCaptureConfig.GROUP.equals(e.getGroup()))
		{
			return;
		}
		bossNames = parseNames(config.bossNames());
		if ("recordAlways".equals(e.getKey()) && !config.recordAlways())
		{
			endSession("record everything turned off");
		}
	}

	@Subscribe
	public void onGameStateChanged(GameStateChanged e)
	{
		if (e.getGameState() == GameState.LOGIN_SCREEN || e.getGameState() == GameState.HOPPING)
		{
			endSession("logged out");
		}
	}

	// ---- session lifecycle --------------------------------------------------------------

	@Subscribe
	public void onGameTick(GameTick e)
	{
		Player me = client.getLocalPlayer();
		if (me == null)
		{
			return;
		}

		NPC boss = findBoss();
		if (writer == null)
		{
			if (boss != null || config.recordAlways())
			{
				startSession(boss != null ? boss.getName() : "manual");
			}
			else
			{
				return;
			}
		}

		if (boss != null || config.recordAlways())
		{
			ticksWithoutBoss = 0;
		}
		else if (++ticksWithoutBoss >= config.endAfterTicks())
		{
			endSession("no boss for " + ticksWithoutBoss + " ticks");
			return;
		}

		writeTick(me);
		sessionTick++;
	}

	private NPC findBoss()
	{
		if (bossNames.isEmpty())
		{
			return null;
		}
		for (NPC npc : worldView().npcs())
		{
			String name = npc.getName();
			// Pets share their boss's name (the Kraken pet is "Kraken"). Followers and pets
			// roaming a POH menagerie both have no combat level, while every boss has one.
			NPCComposition comp = npc.getTransformedComposition();
			if (comp != null && (comp.isFollower() || comp.getCombatLevel() <= 0))
			{
				continue;
			}
			if (name != null && bossNames.contains(name.toLowerCase(Locale.ROOT)) && near(npc))
			{
				return npc;
			}
		}
		return null;
	}

	private void startSession(String boss)
	{
		File dir = config.outputDir().isBlank()
			? new File(RuneLite.RUNELITE_DIR.getParentFile(), "osrs-captures")
			: new File(config.outputDir());
		String slug = boss.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]+", "-").replaceAll("(^-|-$)", "");
		Path path = Paths.get(dir.getPath(), slug + "-" + FILE_STAMP.format(Instant.now()) + ".jsonl");
		try
		{
			writer = new CaptureWriter(gson, path);
		}
		catch (IOException ex)
		{
			log.warn("could not open capture file {}", path, ex);
			return;
		}

		sessionTick = 0;
		ticksWithoutBoss = 0;
		lastPrayers = null;
		seenProjectiles.clear();

		JsonObject o = line("session");
		o.addProperty("format", FORMAT_VERSION);
		o.addProperty("boss", boss);
		o.addProperty("started", Instant.now().toString());
		o.addProperty("revision", client.getRevision());
		o.addProperty("world", client.getWorld());
		o.addProperty("instanced", worldView().isInstance());
		writer.write(o);

		writeEquipment();
		for (NPC npc : worldView().npcs())
		{
			if (near(npc))
			{
				writeNpcSpawn(npc, true);
			}
		}
		log.info("boss capture started: {}", path);
	}

	private void endSession(String reason)
	{
		if (writer == null)
		{
			return;
		}
		JsonObject o = line("end");
		o.addProperty("reason", reason);
		o.addProperty("ticks", sessionTick);
		writer.write(o);
		writer.close();
		log.info("boss capture ended ({}): {}", reason, writer.getPath());
		writer = null;
		seenProjectiles.clear();
	}

	// ---- per-tick snapshot --------------------------------------------------------------

	private void writeTick(Player me)
	{
		JsonObject o = line("tick");

		JsonObject p = new JsonObject();
		addPoint(p, me.getLocalLocation());
		p.addProperty("orientation", me.getOrientation());
		p.addProperty("anim", me.getAnimation());
		p.addProperty("pose", me.getPoseAnimation());
		p.addProperty("hp", client.getBoostedSkillLevel(Skill.HITPOINTS));
		p.addProperty("prayer", client.getBoostedSkillLevel(Skill.PRAYER));
		p.addProperty("run", client.getEnergy());
		addTarget(p, me.getInteracting());
		o.add("player", p);

		List<String> prayers = activePrayers();
		if (!prayers.equals(lastPrayers))
		{
			JsonArray active = new JsonArray();
			prayers.forEach(active::add);
			o.add("prayers", active);
			lastPrayers = prayers;
		}

		JsonArray npcs = new JsonArray();
		for (NPC npc : worldView().npcs())
		{
			if (!near(npc))
			{
				continue;
			}
			JsonObject n = new JsonObject();
			n.addProperty("index", npc.getIndex());
			n.addProperty("id", npc.getId());
			addPoint(n, npc.getLocalLocation());
			n.addProperty("orientation", npc.getOrientation());
			n.addProperty("anim", npc.getAnimation());
			n.addProperty("pose", npc.getPoseAnimation());
			if (npc.getHealthRatio() >= 0)
			{
				n.addProperty("hpRatio", npc.getHealthRatio());
				n.addProperty("hpScale", npc.getHealthScale());
			}
			addTarget(n, npc.getInteracting());
			npcs.add(n);
		}
		o.add("npcs", npcs);

		writer.write(o);
		writer.flush();
	}

	private List<String> activePrayers()
	{
		List<String> active = new ArrayList<>();
		for (Prayer prayer : Prayer.values())
		{
			if (client.getVarbitValue(prayer.getVarbit()) == 1)
			{
				active.add(prayer.name());
			}
		}
		return active;
	}

	// ---- events -------------------------------------------------------------------------

	@Subscribe
	public void onNpcSpawned(NpcSpawned e)
	{
		if (writer != null && near(e.getNpc()))
		{
			writeNpcSpawn(e.getNpc(), false);
		}
	}

	@Subscribe
	public void onNpcDespawned(NpcDespawned e)
	{
		if (writer == null)
		{
			return;
		}
		NPC npc = e.getNpc();
		JsonObject o = line("npc_despawn");
		o.addProperty("index", npc.getIndex());
		o.addProperty("id", npc.getId());
		addPoint(o, npc.getLocalLocation());
		o.addProperty("dead", npc.isDead());
		writer.write(o);
	}

	@Subscribe
	public void onNpcChanged(NpcChanged e)
	{
		if (writer == null)
		{
			return;
		}
		JsonObject o = line("npc_change");
		o.addProperty("index", e.getNpc().getIndex());
		o.addProperty("from", e.getOld() != null ? e.getOld().getId() : -1);
		o.addProperty("to", e.getNpc().getId());
		o.addProperty("name", e.getNpc().getName());
		writer.write(o);
	}

	@Subscribe
	public void onAnimationChanged(AnimationChanged e)
	{
		Actor a = e.getActor();
		if (writer == null || !relevant(a))
		{
			return;
		}
		JsonObject o = line("anim");
		addActor(o, a);
		o.addProperty("anim", a.getAnimation());
		writer.write(o);
	}

	@Subscribe
	public void onGraphicChanged(GraphicChanged e)
	{
		Actor a = e.getActor();
		if (writer == null || !relevant(a))
		{
			return;
		}
		JsonObject o = line("spotanim");
		addActor(o, a);
		JsonArray anims = new JsonArray();
		for (ActorSpotAnim sa : a.getSpotAnims())
		{
			JsonObject g = new JsonObject();
			g.addProperty("id", sa.getId());
			g.addProperty("height", sa.getHeight());
			g.addProperty("startCycle", sa.getStartCycle());
			anims.add(g);
		}
		o.add("gfx", anims);
		writer.write(o);
	}

	@Subscribe
	public void onInteractingChanged(InteractingChanged e)
	{
		if (writer == null || !relevant(e.getSource()))
		{
			return;
		}
		JsonObject o = line("interact");
		addActor(o, e.getSource());
		addTarget(o, e.getTarget());
		writer.write(o);
	}

	@Subscribe
	public void onProjectileMoved(ProjectileMoved e)
	{
		Projectile proj = e.getProjectile();
		if (writer == null || !seenProjectiles.add(proj))
		{
			return;
		}
		JsonObject o = line("projectile");
		o.addProperty("id", proj.getId());
		o.addProperty("startCycle", proj.getStartCycle());
		o.addProperty("endCycle", proj.getEndCycle());
		o.addProperty("cycle", client.getGameCycle());
		o.addProperty("slope", proj.getSlope());
		o.addProperty("startHeight", proj.getStartHeight());
		o.addProperty("endHeight", proj.getEndHeight());
		JsonObject from = new JsonObject();
		addWorldPoint(from, proj.getSourcePoint());
		if (proj.getSourceActor() != null)
		{
			addActor(from, proj.getSourceActor());
		}
		o.add("from", from);
		JsonObject to = new JsonObject();
		addWorldPoint(to, proj.getTargetPoint());
		if (proj.getTargetActor() != null)
		{
			addActor(to, proj.getTargetActor());
		}
		o.add("to", to);
		writer.write(o);
	}

	@Subscribe
	public void onGraphicsObjectCreated(GraphicsObjectCreated e)
	{
		if (writer == null)
		{
			return;
		}
		GraphicsObject g = e.getGraphicsObject();
		JsonObject o = line("graphics_object");
		o.addProperty("id", g.getId());
		o.addProperty("startCycle", g.getStartCycle());
		o.addProperty("height", g.getZ());
		addPoint(o, g.getLocation());
		writer.write(o);
	}

	@Subscribe
	public void onGameObjectSpawned(GameObjectSpawned e)
	{
		writeObject("object_spawn", e.getGameObject());
	}

	@Subscribe
	public void onGameObjectDespawned(GameObjectDespawned e)
	{
		writeObject("object_despawn", e.getGameObject());
	}

	private void writeObject(String type, GameObject obj)
	{
		if (writer == null || !near(obj.getLocalLocation()))
		{
			return;
		}
		JsonObject o = line(type);
		o.addProperty("id", obj.getId());
		addPoint(o, obj.getLocalLocation());
		o.addProperty("orientation", obj.getOrientation());
		writer.write(o);
	}

	@Subscribe
	public void onHitsplatApplied(HitsplatApplied e)
	{
		if (writer == null || !relevant(e.getActor()))
		{
			return;
		}
		Hitsplat h = e.getHitsplat();
		JsonObject o = line("hitsplat");
		addActor(o, e.getActor());
		o.addProperty("hitsplatType", h.getHitsplatType());
		o.addProperty("amount", h.getAmount());
		o.addProperty("mine", h.isMine());
		writer.write(o);
	}

	@Subscribe
	public void onActorDeath(ActorDeath e)
	{
		if (writer == null || !relevant(e.getActor()))
		{
			return;
		}
		JsonObject o = line("death");
		addActor(o, e.getActor());
		writer.write(o);
	}

	@Subscribe
	public void onSoundEffectPlayed(SoundEffectPlayed e)
	{
		if (writer == null)
		{
			return;
		}
		JsonObject o = line("sound");
		o.addProperty("id", e.getSoundId());
		o.addProperty("delay", e.getDelay());
		if (e.getSource() != null)
		{
			addActor(o, e.getSource());
		}
		writer.write(o);
	}

	@Subscribe
	public void onAreaSoundEffectPlayed(AreaSoundEffectPlayed e)
	{
		if (writer == null)
		{
			return;
		}
		JsonObject o = line("area_sound");
		o.addProperty("id", e.getSoundId());
		o.addProperty("delay", e.getDelay());
		o.addProperty("range", e.getRange());
		addPoint(o, LocalPoint.fromScene(e.getSceneX(), e.getSceneY(), worldView()));
		if (e.getSource() != null)
		{
			addActor(o, e.getSource());
		}
		writer.write(o);
	}

	@Subscribe
	public void onOverheadTextChanged(OverheadTextChanged e)
	{
		if (writer == null || !(e.getActor() instanceof NPC) || !relevant(e.getActor()))
		{
			return;
		}
		JsonObject o = line("overhead_text");
		addActor(o, e.getActor());
		o.addProperty("text", e.getOverheadText());
		writer.write(o);
	}

	@Subscribe
	public void onChatMessage(ChatMessage e)
	{
		// Game and dialogue messages only; other players' chat is never recorded.
		if (writer == null || !CHAT_TYPES.contains(e.getType()))
		{
			return;
		}
		JsonObject o = line("chat");
		o.addProperty("chatType", e.getType().name());
		o.addProperty("text", e.getMessage());
		writer.write(o);
	}

	@Subscribe
	public void onItemContainerChanged(ItemContainerChanged e)
	{
		if (writer != null && e.getContainerId() == InventoryID.WORN)
		{
			writeEquipment();
		}
	}

	// ---- helpers ------------------------------------------------------------------------

	private void writeNpcSpawn(NPC npc, boolean present)
	{
		JsonObject o = line("npc_spawn");
		o.addProperty("index", npc.getIndex());
		o.addProperty("id", npc.getId());
		o.addProperty("name", npc.getName());
		o.addProperty("present", present);
		NPCComposition comp = npc.getTransformedComposition();
		if (comp != null)
		{
			o.addProperty("combatLevel", comp.getCombatLevel());
			o.addProperty("size", comp.getSize());
		}
		addPoint(o, npc.getLocalLocation());
		writer.write(o);
	}

	private void writeEquipment()
	{
		ItemContainer worn = client.getItemContainer(InventoryID.WORN);
		if (worn == null)
		{
			return;
		}
		JsonArray items = new JsonArray();
		for (Item item : worn.getItems())
		{
			items.add(item.getId());
		}
		JsonObject o = line("equipment");
		o.add("items", items);
		writer.write(o);
	}

	private JsonObject line(String type)
	{
		JsonObject o = new JsonObject();
		o.addProperty("type", type);
		o.addProperty("tick", sessionTick);
		o.addProperty("cycle", client.getGameCycle());
		return o;
	}

	/** Adds x/y/plane as real-world coordinates, undoing instance remapping. */
	private void addPoint(JsonObject o, LocalPoint lp)
	{
		if (lp == null)
		{
			return;
		}
		WorldPoint wp = WorldPoint.fromLocalInstance(client, lp);
		o.addProperty("x", wp.getX());
		o.addProperty("y", wp.getY());
		o.addProperty("plane", wp.getPlane());
	}

	/** Same as addPoint, for a WorldPoint the server sent in instance coordinates. */
	private void addWorldPoint(JsonObject o, WorldPoint wp)
	{
		if (wp == null)
		{
			return;
		}
		LocalPoint lp = LocalPoint.fromWorld(worldView(), wp);
		if (lp != null)
		{
			addPoint(o, lp);
			return;
		}
		o.addProperty("x", wp.getX());
		o.addProperty("y", wp.getY());
		o.addProperty("plane", wp.getPlane());
	}

	private void addActor(JsonObject o, Actor a)
	{
		if (a instanceof NPC)
		{
			o.addProperty("actor", "npc");
			o.addProperty("index", ((NPC) a).getIndex());
			o.addProperty("npcId", ((NPC) a).getId());
		}
		else if (a == client.getLocalPlayer())
		{
			o.addProperty("actor", "me");
		}
		else
		{
			o.addProperty("actor", "player");
		}
	}

	private void addTarget(JsonObject o, Actor target)
	{
		if (target == null)
		{
			return;
		}
		JsonObject t = new JsonObject();
		addActor(t, target);
		o.add("target", t);
	}

	/** The local player, or an NPC in range. Other players are left out. */
	private boolean relevant(Actor a)
	{
		if (a == client.getLocalPlayer())
		{
			return true;
		}
		return a instanceof NPC && near(a);
	}

	private boolean near(Actor a)
	{
		return a != null && near(a.getLocalLocation());
	}

	private boolean near(LocalPoint lp)
	{
		Player me = client.getLocalPlayer();
		if (lp == null || me == null || me.getLocalLocation() == null)
		{
			return false;
		}
		LocalPoint mine = me.getLocalLocation();
		int dx = Math.abs(lp.getSceneX() - mine.getSceneX());
		int dy = Math.abs(lp.getSceneY() - mine.getSceneY());
		return Math.max(dx, dy) <= config.radius();
	}

	private WorldView worldView()
	{
		return client.getTopLevelWorldView();
	}

	private static Set<String> parseNames(String csv)
	{
		return Arrays.stream(csv.split(","))
			.map(s -> s.trim().toLowerCase(Locale.ROOT))
			.filter(s -> !s.isEmpty())
			.collect(Collectors.toSet());
	}
}
