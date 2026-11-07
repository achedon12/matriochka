package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.ContainerTags;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.gear.GearClasses;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.rules.WorldRules;
import java.util.Set;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.biome.v1.ModificationPhase;
import net.fabricmc.fabric.api.entity.event.v1.ServerEntityLevelChangeEvents;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.NonNullList;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.portal.TeleportTransition;
import net.minecraft.world.phys.Vec3;

/** Lifecycle hooks: first join, the doll of life, death chest, cradles, progression gates and periodic scans. */
public final class Events {
	private Events() {}

	/** The Doll Peddler wanders the Surface like a trader: now and then he turns up near a player, and leaves two days later. */
	public static void peddler(ServerLevel level) {
		var type = ModContent.entity("doll_peddler");
		for (ServerPlayer p : level.players()) {
			if (p.isSpectator() || level.getRandom().nextInt(4) != 0) continue;
			if (!level.getEntitiesOfClass(fr.achedon12.matriochka.entity.MatrioNpc.class, p.getBoundingBox().inflate(128), e -> e.getType() == type).isEmpty()) continue;
			double a = level.getRandom().nextDouble() * Math.PI * 2, r = 24 + level.getRandom().nextInt(16);
			BlockPos at = level.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
				BlockPos.containing(p.getX() + Math.cos(a) * r, p.getY(), p.getZ() + Math.sin(a) * r));
			if (!level.getFluidState(at.below()).isEmpty() || !level.getBlockState(at.below()).isSolid()) continue;
			var e = type.create(level, net.minecraft.world.entity.EntitySpawnReason.EVENT);
			if (e == null) continue;
			e.setPos(at.getX() + 0.5, at.getY(), at.getZ() + 0.5);
			e.addTag("wanderer");
			level.addFreshEntity(e);
			return;
		}
	}

	/** A world whose block was broken stays unstable for 20 minutes: half as many creatures again roam around its players. */
	private static void unstable(net.minecraft.server.MinecraftServer server) {
		MatrioData data = MatrioData.get(server);
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			int w = Worlds.number(p.level());
			if (w <= 0 || p.isSpectator() || !(p.level() instanceof ServerLevel level)) continue;
			if (data.worldEntry(data.groupOf(p.getUUID()), w).getLongOr("unstable_until", 0L) <= level.getGameTime()) continue;
			if (level.getRandom().nextInt(2) != 0) continue;
			spawnNear(level, p, w);
		}
	}

	/** Wild and cursed worlds call more creatures around their players (a spawn rate above 1, see Variants). */
	private static void variantSpawns(net.minecraft.server.MinecraftServer server) {
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			int w = Worlds.number(p.level());
			if (w <= 0 || w > 10 || p.isSpectator() || !(p.level() instanceof ServerLevel level)) continue;
			float extra = Variants.of(p).spawn() - 1f;
			if (extra > 0 && level.getRandom().nextFloat() < extra) spawnNear(level, p, w);
		}
	}

	/** One creature of the world, 14 to 24 blocks from a player, unless there are already many around. */
	private static void spawnNear(ServerLevel level, ServerPlayer p, int w) {
		var pool = Content.MOBS.stream().filter(m -> m.world() == w && !m.elite() && m.aquatic() == (w == 7)).toList();
		if (pool.isEmpty()) return;
		var def = pool.get(level.getRandom().nextInt(pool.size()));
		if (level.getEntitiesOfClass(fr.achedon12.matriochka.entity.MatrioMob.class, p.getBoundingBox().inflate(32)).size() > 12) return;
		double a = level.getRandom().nextDouble() * Math.PI * 2, r = 14 + level.getRandom().nextInt(10);
		BlockPos at = BlockPos.containing(p.getX() + Math.cos(a) * r, p.getY(), p.getZ() + Math.sin(a) * r);
		// find a free spot near the player's height
		BlockPos spot = null;
		for (int dy = 4; dy >= -6 && spot == null; dy--) {
			BlockPos q = at.above(dy);
			if (level.getBlockState(q.below()).isSolid() && level.getBlockState(q).isAir() && level.getBlockState(q.above()).isAir()) spot = q;
		}
		if (spot == null && w == 7 && level.getFluidState(at).isSource()) spot = at;
		if (spot == null) return;
		var e = ModContent.entity(def.id()).create(level, net.minecraft.world.entity.EntitySpawnReason.EVENT);
		if (e == null) return;
		e.setPos(spot.getX() + 0.5, spot.getY(), spot.getZ() + 0.5);
		level.addFreshEntity(e);
	}

	public static void init() {
		WorldZero.init();
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			WorldRules.serverTick(server);
			WorldZero.tick(server);
			Rituals.tick(server);
			if (server.overworld().getGameTime() % 100 == 0) for (ServerPlayer p : server.getPlayerList().getPlayers()) scanInventory(p);
			if (server.overworld().getGameTime() % 4800 == 2400) peddler(server.overworld());
			if (server.overworld().getGameTime() % 200 == 100) unstable(server);
			if (server.overworld().getGameTime() % 200 == 150) variantSpawns(server);
			ScaleLinks.tick(server);
		});

		ServerLifecycleEvents.SERVER_STOPPED.register(server -> Rituals.clear());

		ServerPlayerEvents.JOIN.register(player -> {
			PlayerState ps = PlayerState.of(player);
			MatrioData.get(player.level().getServer()).groupOf(player.getUUID());
			if (!ps.has("scroll_given")) {
				ps.set("scroll_given", true);
				player.getInventory().add(new ItemStack(ModContent.item("artisan_scroll")));
				fr.achedon12.matriochka.net.Net.openJournal(player, true);
			}
			Cycles.catchUp(player);
			Endings.applyLasting(player);
			ps.sync();
		});

		// Doll of life, then death chest.
		ServerPlayerEvents.ALLOW_DEATH.register((player, source, amount) -> {
			PlayerState ps = PlayerState.of(player);
			long now = player.level().getGameTime();
			if (!Config.hardcore() && ps.dollLayers() > 0 && now - ps.tag().getLongOr("last_revive", -10000) >= 1200) {
				ps.setDoll(ps.dollLayers() - 1, ps.dollMax());
				CycleStats.add(player, "lost", 1);
				ps.tag().putLong("last_revive", now);
				fr.achedon12.matriochka.entity.BossFeats.markNear(player, "layer");
				player.setHealth(player.getMaxHealth() * 0.5f);
				player.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 100, 4));
				player.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 100, 1));
				ServerLevel l = (ServerLevel) player.level();
				l.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, player.getX(), player.getY() + 1, player.getZ(), 60, 0.5, 1, 0.5, 0.4);
				l.playSound(null, player.blockPosition(), fr.achedon12.matriochka.content.Sounds.DOLL_OF_LIFE_BREAK, SoundSource.PLAYERS, 1.2f, 1f);
				player.sendOverlayMessage(Component.translatable("message.matriochka.doll_broke", ps.dollLayers()).withStyle(ChatFormatting.GOLD));
				return false;
			}
			boolean keep = player.level().getGameRules().get(net.minecraft.world.level.gamerules.GameRules.KEEP_INVENTORY);
			if (Config.keepInventory() && !keep) Deaths.keepInventory(player);
			else if (Worlds.isModWorld(player.level()) && !keep) deathChest(player);
			ps.tag().putInt("died_in", Worlds.number(player.level()));
			fr.achedon12.matriochka.entity.BossFeats.markNear(player, "died");
			return true;
		});

		ServerPlayerEvents.AFTER_RESPAWN.register((oldP, player, alive) -> {
			Deaths.afterRespawn(player, alive);
			Endings.applyLasting(player);
			if (Config.hardcore() && !alive) return;
			PlayerState ps = PlayerState.of(player);
			int w = ps.tag().getIntOr("died_in", 0);
			if (w <= 0 || alive) return;
			var c = ps.tag().getCompoundOrEmpty("cradle_" + w);
			ServerLevel level = player.level().getServer().getLevel(Worlds.key(w));
			if (level == null || !c.contains("x")) return;
			BlockPos pos = new BlockPos(c.getIntOr("x", 0), c.getIntOr("y", 0), c.getIntOr("z", 0));
			if (!level.getEntitiesOfClass(fr.achedon12.matriochka.entity.MatrioBoss.class, new net.minecraft.world.phys.AABB(pos).inflate(48)).isEmpty()) {
				player.sendSystemMessage(Component.translatable("message.matriochka.cradle_boss"));
				return;
			}
			if (level.getBlockEntity(pos) instanceof DataBlockEntity be && be.data().getIntOr("charges", 0) > 0) {
				be.data().putInt("charges", be.data().getIntOr("charges", 0) - 1);
				be.changed();
				player.teleport(new TeleportTransition(level, Vec3.atBottomCenterOf(pos.above()), Vec3.ZERO, 0, 0, Set.of(), TeleportTransition.DO_NOTHING));
				player.sendSystemMessage(Component.translatable("message.matriochka.cradle_used", be.data().getIntOr("charges", 0)));
			}
		});

		ServerLivingEntityEvents.AFTER_DAMAGE.register((entity, source, base, taken, blocked) -> {
			if (entity instanceof ServerPlayer hurt && source.is(net.minecraft.tags.DamageTypeTags.IS_LIGHTNING)) {
				fr.achedon12.matriochka.entity.BossFeats.markNear(hurt, "bolt");
			}
			if (source.getEntity() instanceof ServerPlayer p) {
				float steal = GearClasses.lifeSteal(p);
				if (steal > 0) p.heal(taken * steal);
				if (source.getDirectEntity() == p && taken > 0) impact(p, entity, taken);
			}
		});

		// A creature hooked into the void.
		ServerLivingEntityEvents.AFTER_DEATH.register((entity, source) -> {
			if (!source.is(net.minecraft.world.damagesource.DamageTypes.FELL_OUT_OF_WORLD) || !(entity.level() instanceof ServerLevel l)) return;
			java.util.UUID by = fr.achedon12.matriochka.item.Hooked.by(entity, l.getGameTime());
			if (by != null && l.getServer().getPlayerList().getPlayer(by) instanceof ServerPlayer hooker) Achievements.grant(hooker, "hook_void");
		});

		// Gates: enchanting and anvils before world 2, cracked doll placement.
		UseBlockCallback.EVENT.register((player, level, hand, hit) -> {
			if (!(player instanceof ServerPlayer sp)) return InteractionResult.PASS;
			var state = level.getBlockState(hit.getBlockPos());
			ItemStack held = player.getItemInHand(hand);
			if (held.is(ModContent.item("cracked_doll"))) {
				return fr.achedon12.matriochka.block.Blocks2.placeCrackedDoll(sp, held, hit.getBlockPos().relative(hit.getDirection())) ? InteractionResult.SUCCESS : InteractionResult.FAIL;
			}
			if (!Config.gates()) return InteractionResult.PASS;
			boolean enchant = state.is(Blocks.ENCHANTING_TABLE) || state.is(Blocks.ANVIL) || state.is(Blocks.CHIPPED_ANVIL) || state.is(Blocks.DAMAGED_ANVIL);
			if (enchant && !MatrioData.get(sp.level().getServer()).defeated(sp, 2) && !sp.isCreative()) {
				sp.sendOverlayMessage(Component.translatable("message.matriochka.gate.enchant").withStyle(ChatFormatting.RED));
				return InteractionResult.FAIL;
			}
			return InteractionResult.PASS;
		});

		// Nether after world 2, End after world 8.
		ServerEntityLevelChangeEvents.AFTER_PLAYER_CHANGE_LEVEL.register((player, from, to) -> {
			if (!Config.gates() || player.isCreative()) return;
			MatrioData data = MatrioData.get(player.level().getServer());
			boolean blocked = (to.dimension() == Level.NETHER && !data.defeated(player, 2)) || (to.dimension() == Level.END && !data.defeated(player, 8));
			if (blocked) {
				player.sendSystemMessage(Component.translatable(to.dimension() == Level.NETHER ? "message.matriochka.gate.nether" : "message.matriochka.gate.end").withStyle(ChatFormatting.RED));
				ServerLevel back = player.level().getServer().overworld();
				BlockPos spawn = back.getRespawnData().pos();
				player.teleport(new TeleportTransition(back, Vec3.atBottomCenterOf(Travel.findSafe(back, back.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING, spawn))),
					Vec3.ZERO, 0, 0, Set.of(), TeleportTransition.DO_NOTHING));
			}
		});

		// Diamonds only from world 5: none in the loot chests of vanilla structures either.
		net.fabricmc.fabric.api.loot.v3.LootTableEvents.MODIFY_DROPS.register((table, context, drops) -> {
			var key = table.unwrapKey();
			if (key.isEmpty()) return;
			var id = key.get().identifier();
			if (!id.getNamespace().equals("minecraft") || !id.getPath().startsWith("chests/")) return;
			drops.removeIf(st -> st.is(net.minecraft.world.item.Items.DIAMOND) || st.is(net.minecraft.world.item.Items.DIAMOND_BLOCK));
		});

		// Diamonds only from world 5: remove diamond ores from the surface.
		BiomeModifications.create(Matriochka.id("no_surface_diamonds")).add(ModificationPhase.REMOVALS, BiomeSelectors.foundInOverworld(), ctx -> {
			for (String f : new String[]{"ore_diamond", "ore_diamond_medium", "ore_diamond_large", "ore_diamond_buried"}) {
				ctx.getGenerationSettings().removeFeature(ResourceKey.create(Registries.PLACED_FEATURE, Identifier.withDefaultNamespace(f)));
			}
		});
	}

	private static void deathChest(ServerPlayer player) {
		ServerLevel level = (ServerLevel) player.level();
		BlockPos pos = player.blockPosition();
		if (fr.achedon12.matriochka.entity.MatrioBoss.inArena(level, pos)) {
			BlockPos c = Worlds.parcelCenter(Worlds.parcelOf(pos));
			pos = new BlockPos(pos.getX(), pos.getY(), c.getZ() + fr.achedon12.matriochka.entity.MatrioBoss.stageExitZ(level));
		}
		pos = Travel.findSafe(level, pos);
		NonNullList<ItemStack> items = NonNullList.withSize(54, ItemStack.EMPTY);
		int k = 0;
		var inv = player.getInventory();
		for (int i = 0; i < inv.getContainerSize() && k < 54; i++) {
			ItemStack s = inv.getItem(i);
			if (!s.isEmpty() && !s.is(ModContent.item("artisan_journal")) && !s.is(ModContent.item("artisan_scroll"))) {
				items.set(k++, s.copy());
				inv.setItem(i, ItemStack.EMPTY);
			}
		}
		if (k == 0) return;
		level.setBlock(pos, ModContent.block("death_chest").defaultBlockState(), 3);
		if (level.getBlockEntity(pos) instanceof DataBlockEntity be) {
			ContainerTags.save(be.data(), level.registryAccess(), items);
			be.changed();
		}
		player.sendSystemMessage(Component.translatable("message.matriochka.death_chest", pos.getX(), pos.getY(), pos.getZ()));
	}

	/** Every 5 s: obtain-quests, journal pages and hidden dolls in the inventory. */
	private static void scanInventory(ServerPlayer p) {
		PlayerState ps = PlayerState.of(p);
		var inv = p.getInventory();
		for (Defs.QuestDef q : Content.QUESTS) {
			// deliveries are handed to the peoples (QuestHooks.deliver), only "obtain" quests count what you carry
			if (!q.objKind().equals("obtain") || Quests.done(ps, q)) continue;
			var item = ModContent.itemOrNull(q.objTarget());
			if (item == null) continue;
			int n = fr.achedon12.matriochka.block.Stations.count(inv, item);
			int have = ps.counter("obtain:" + q.objTarget());
			if (n > have) ps.progress("obtain", q.objTarget(), n - have);
		}
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			if (s.is(ModContent.item("journal_page"))) {
				var cd = s.get(net.minecraft.core.component.DataComponents.CUSTOM_DATA);
				if (cd != null) {
					var t = cd.copyTag();
					int w = t.getIntOr("world", 1), idx = t.getIntOr("index", 0);
					if (ps.addPage(w, idx)) {
						p.sendSystemMessage(Component.translatable("message.matriochka.page_found", w, idx + 1).withStyle(ChatFormatting.YELLOW));
						if (ps.pages(w) >= 5) Achievements.grantPages(p, w);
					}
				}
			}
		}
		int dolls = 0;
		for (int w = 1; w <= 10; w++) if (fr.achedon12.matriochka.block.Stations.count(inv, ModContent.item("hidden_doll_" + w)) > 0) {
			dolls++;
			// the Journal's collection remembers every hidden doll this player has held
			if (!ps.has("found_doll_" + w)) ps.set("found_doll_" + w, true);
		}
		// dolls already nested count too
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			if (s.is(ModContent.item("nested_dolls")) || s.is(ModContent.item("whole_matryoshka"))) dolls += fr.achedon12.matriochka.item.Nesting.depth(s);
		}
		CycleStats.max(p, "dolls", dolls);
		if (dolls >= 10) Achievements.grant(p, "all_dolls");
		if (p.isFallFlying() || (p.getY() > 220 && Worlds.number(p.level()) == 4)) Achievements.grant(p, "high_fall");
		if (Worlds.number(p.level()) == 10) {
			ps.progress("enter", "world_10", 1);
		}
		if (Player.class.isInstance(p)) ps.sync();
	}

	/**
	 * The weight of the player's own blows: a heavy hit or a critical one jolts the attacker's camera a little (scaled
	 * by the comfort slider), a weapon of the worlds sprays its world's matter where it lands, and a heavy blow rings
	 * with its world's sound.
	 */
	private static void impact(ServerPlayer p, net.minecraft.world.entity.LivingEntity target, float taken) {
		if (!(p.level() instanceof ServerLevel level)) return;
		boolean crit = p.fallDistance > 0 && !p.onGround() && !p.onClimbable() && !p.isInWater() && !p.isPassenger();
		boolean heavy = crit || taken >= 7;
		if (heavy) fr.achedon12.matriochka.net.Cues.shake(p, Math.min(0.45f, 0.15f + taken / 40f), crit ? 5 : 4);
		ItemStack held = p.getMainHandItem();
		fr.achedon12.matriochka.content.Defs.ItemDef def = ModContent.def(ModContent.idOf(held.getItem()));
		if (def == null || def.world() < 1 || def.world() > 10 || !(def.kind().equals("weapon") || def.kind().equals("tool"))) return;
		int w = def.world();
		var at = target.position().add(0, target.getBbHeight() * 0.6, 0);
		net.minecraft.core.particles.SimpleParticleType matter = switch (w) {
			case 1 -> fr.achedon12.matriochka.content.Particles.SPORE;
			case 2 -> fr.achedon12.matriochka.content.Particles.EMBER;
			case 3 -> fr.achedon12.matriochka.content.Particles.COLD_DUST;
			case 4 -> fr.achedon12.matriochka.content.Particles.STORM_SPARK;
			case 5 -> fr.achedon12.matriochka.content.Particles.SHADOW_WISP;
			case 6 -> fr.achedon12.matriochka.content.Particles.MIRROR_SHARD;
			case 7 -> fr.achedon12.matriochka.content.Particles.BUBBLE;
			case 8 -> fr.achedon12.matriochka.content.Particles.PETAL;
			case 9 -> fr.achedon12.matriochka.content.Particles.GRIT;
			default -> fr.achedon12.matriochka.content.Particles.THREAD_SCRAP;
		};
		level.sendParticles(matter, at.x, at.y, at.z, heavy ? 14 : 6, 0.3, 0.35, 0.3, heavy ? 0.12 : 0.05);
		if (!heavy) return;
		net.minecraft.sounds.SoundEvent ring = switch (w) {
			case 1 -> SoundEvents.SLIME_ATTACK;
			case 2 -> SoundEvents.FIRECHARGE_USE;
			case 3 -> SoundEvents.CHAIN_BREAK;
			case 4 -> SoundEvents.TRIDENT_HIT;
			case 5 -> SoundEvents.SCULK_CLICKING;
			case 6 -> SoundEvents.AMETHYST_BLOCK_HIT;
			case 7 -> SoundEvents.BUBBLE_COLUMN_UPWARDS_INSIDE;
			case 8 -> SoundEvents.AZALEA_LEAVES_BREAK;
			case 9 -> SoundEvents.DEEPSLATE_BREAK;
			default -> SoundEvents.WOOL_BREAK;
		};
		level.playSound(null, target.blockPosition(), ring, SoundSource.PLAYERS, 0.7f, 0.9f + p.getRandom().nextFloat() * 0.3f);
	}
}
