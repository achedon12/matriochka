package fr.achedon12.matriochka.rules;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseTorchBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CampfireBlock;
import net.minecraft.world.level.block.LightBlock;
import net.minecraft.world.level.block.RedstoneLampBlock;
import net.minecraft.world.level.block.RedStoneOreBlock;
import net.minecraft.world.level.block.RedstoneTorchBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

/**
 * World 5: the lights players bring burn out. A placed torch, lantern, candle, campfire or glowing block lasts one
 * minute, smokes for its last five seconds, then dies: torches crumble to a stick, campfires and candles are snuffed
 * (relight them and the minute starts again), glowing blocks turn to Spent Glow, anything else falls back as an item.
 * The Deep's own blocks never burn out, and a lit Solar Lantern carries its glow with the player.
 */
public final class Burnout {
	private Burnout() {}

	/** How long a brought light lasts, in ticks (60 s, as in the design rules). */
	public static final long LIFE = 20 * 60;
	/** The smoking warning before it dies. */
	public static final long WARN = 20 * 5;
	/** Chunks scanned around each player. */
	private static final int RADIUS = 2;
	/** Brightness of the Solar Lantern's glow. */
	private static final int LANTERN_LEVEL = 14;

	private static Map<String, Defs.BlockDef> defs;

	/** Where the glow of each player's lit lantern currently is. */
	private static final Map<UUID, Glow> GLOWS = new HashMap<>();

	private record Glow(ResourceKey<Level> level, BlockPos pos) {}

	private static Defs.BlockDef def(String id) {
		if (defs == null) {
			defs = new HashMap<>();
			for (Defs.BlockDef d : Content.BLOCKS) defs.put(d.id(), d);
		}
		return defs.get(id);
	}

	/** Whether a placed block is a light the Deep will snuff out (lit or not yet lit, like a candle). */
	public static boolean burns(BlockState s) {
		Block b = s.getBlock();
		if (b == Blocks.LIGHT) return false;
		if (b instanceof RedstoneTorchBlock || b instanceof RedstoneLampBlock || b instanceof RedStoneOreBlock) return false;
		if (s.hasProperty(BlockStateProperties.POWERED)) return false;
		Identifier id = BuiltInRegistries.BLOCK.getKey(b);
		if (id.getNamespace().equals(Matriochka.MOD_ID)) {
			Defs.BlockDef d = def(id.getPath());
			return d != null && d.world() != 5 && "glow".equals(d.style());
		}
		if (s.hasBlockEntity() && !(b instanceof CampfireBlock)) return false;
		return s.getLightEmission() > 0 || s.hasProperty(BlockStateProperties.LIT);
	}

	/** Once per second per player in a World 5 rule zone: ages the brought lights around them. */
	public static int scan(ServerLevel level, ServerPlayer p, long now) {
		int burnt = 0;
		int pcx = SectionPos.blockToSectionCoord(p.getBlockX()), pcz = SectionPos.blockToSectionCoord(p.getBlockZ());
		for (int cx = pcx - RADIUS; cx <= pcx + RADIUS; cx++) {
			for (int cz = pcz - RADIUS; cz <= pcz + RADIUS; cz++) {
				PlacedBlocks.Marks m = PlacedBlocks.marks(level, cx, cz);
				if (m == null || m.lights().isEmpty()) continue;
				boolean dirty = false;
				Iterator<it.unimi.dsi.fastutil.longs.Long2LongMap.Entry> it = m.lights().long2LongEntrySet().iterator();
				while (it.hasNext()) {
					var e = it.next();
					BlockPos pos = BlockPos.of(e.getLongKey());
					BlockState s = level.getBlockState(pos);
					long since = e.getLongValue();
					if (since == PlacedBlocks.LANTERN) {
						// a lantern glow left behind (logout, restart): clear it unless it is someone's current glow
						if (!isCurrentGlow(level, pos)) {
							if (s.is(Blocks.LIGHT)) level.setBlock(pos, Blocks.AIR.defaultBlockState(), Block.UPDATE_ALL);
							it.remove();
							dirty = true;
						}
						continue;
					}
					if (s.isAir() || !burns(s)) {
						it.remove();
						dirty = true;
						continue;
					}
					if (s.hasProperty(BlockStateProperties.LIT) && !s.getValue(BlockStateProperties.LIT)) {
						// unlit: the minute only counts while it burns
						if (since != now) {
							e.setValue(now);
							dirty = true;
						}
						continue;
					}
					long age = now - since;
					if (age >= LIFE) {
						if (extinguish(level, pos, s)) {
							e.setValue(now);
						} else {
							it.remove();
						}
						dirty = true;
						burnt++;
					} else if (age >= LIFE - WARN) {
						level.sendParticles(ParticleTypes.SMOKE, pos.getX() + 0.5, pos.getY() + 0.7, pos.getZ() + 0.5, 4, 0.15, 0.1, 0.15, 0.01);
						if (age < LIFE - WARN + 20) level.playSound(null, pos, SoundEvents.CANDLE_EXTINGUISH, SoundSource.BLOCKS, 0.4f, 0.6f);
					}
				}
				if (dirty) PlacedBlocks.dirty(level, cx, cz);
			}
		}
		if (burnt > 0 && !PlayerState.of(p).has("burnout_told")) {
			PlayerState.of(p).set("burnout_told", true);
			p.sendSystemMessage(Component.translatable("message.matriochka.rule.burnout").withStyle(ChatFormatting.DARK_AQUA));
		}
		return burnt;
	}

	/** Kills one light. Returns true when the block stays in place (snuffed, can be relit), false when it is gone. */
	public static boolean extinguish(ServerLevel level, BlockPos pos, BlockState s) {
		level.sendParticles(ParticleTypes.LARGE_SMOKE, pos.getX() + 0.5, pos.getY() + 0.6, pos.getZ() + 0.5, 6, 0.2, 0.2, 0.2, 0.01);
		level.playSound(null, pos, SoundEvents.FIRE_EXTINGUISH, SoundSource.BLOCKS, 0.6f, 1.2f);
		if (s.hasProperty(BlockStateProperties.LIT)) {
			level.setBlock(pos, s.setValue(BlockStateProperties.LIT, false), Block.UPDATE_ALL);
			return true;
		}
		if (s.getBlock() instanceof BaseTorchBlock) {
			level.setBlock(pos, Blocks.AIR.defaultBlockState(), Block.UPDATE_ALL);
			Block.popResource(level, pos, new ItemStack(Items.STICK));
			return false;
		}
		if (s.isCollisionShapeFullBlock(level, pos)) {
			level.setBlock(pos, ModContent.block("spent_glow").defaultBlockState(), Block.UPDATE_ALL);
			return false;
		}
		level.destroyBlock(pos, true);
		return false;
	}

	// ---------------------------------------------------------------- the Solar Lantern's glow

	private static boolean isCurrentGlow(ServerLevel level, BlockPos pos) {
		for (Glow g : GLOWS.values()) if (g.level == level.dimension() && g.pos.equals(pos)) return true;
		return false;
	}

	/**
	 * Every few ticks: a player holding a lit Solar Lantern in a World 5 rule zone carries an invisible light block at
	 * eye height; it is removed when they move on, leave, or the lantern runs out.
	 */
	public static void tickGlows(MinecraftServer server, java.util.function.Predicate<ServerPlayer> inDark) {
		long now = server.overworld().getGameTime();
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			boolean lit = !p.isSpectator() && inDark.test(p) && PlayerState.of(p).flagActive("lantern", now);
			Glow old = GLOWS.get(p.getUUID());
			if (!lit) {
				if (old != null) clear(server, p.getUUID(), old);
				continue;
			}
			ServerLevel level = (ServerLevel) p.level();
			BlockPos want = BlockPos.containing(p.getX(), p.getEyeY(), p.getZ());
			if (!level.getBlockState(want).isAir() && !level.getBlockState(want).is(Blocks.LIGHT)) want = p.blockPosition();
			if (old != null && old.level == level.dimension() && old.pos.equals(want)) continue;
			if (old != null) clear(server, p.getUUID(), old);
			BlockState at = level.getBlockState(want);
			if (!at.isAir()) continue;
			level.setBlock(want, Blocks.LIGHT.defaultBlockState().setValue(LightBlock.LEVEL, LANTERN_LEVEL), Block.UPDATE_CLIENTS);
			PlacedBlocks.markLantern(level, want);
			GLOWS.put(p.getUUID(), new Glow(level.dimension(), want));
		}
		// players who left the server
		GLOWS.entrySet().removeIf(e -> {
			if (server.getPlayerList().getPlayer(e.getKey()) != null) return false;
			remove(server, e.getValue());
			return true;
		});
	}

	private static void clear(MinecraftServer server, UUID id, Glow g) {
		remove(server, g);
		GLOWS.remove(id);
	}

	private static void remove(MinecraftServer server, Glow g) {
		ServerLevel level = server.getLevel(g.level);
		if (level == null || !level.isLoaded(g.pos)) return;
		if (level.getBlockState(g.pos).is(Blocks.LIGHT)) level.setBlock(g.pos, Blocks.AIR.defaultBlockState(), Block.UPDATE_CLIENTS);
		PlacedBlocks.forgetLight(level, g.pos);
	}

	/** Forgets every glow (server stop); the records left in the chunks clean the blocks up later. */
	public static void clearAll() {
		GLOWS.clear();
	}

	/** The glow currently carried by this player, if any (tests). */
	public static BlockPos glowOf(ServerPlayer p) {
		Glow g = GLOWS.get(p.getUUID());
		return g == null ? null : g.pos;
	}
}
