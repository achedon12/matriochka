package fr.achedon12.matriochka.content;

/** Plain data records filled by the generated {@link Content} class. */
public final class Defs {
	private Defs() {}

	public record WorldDef(int n, String rule, String tier, int primary, int accent, boolean ceiling) {}

	public record ItemDef(String id, int world, String kind, String rarity, String piece, String set) {}

	public record BlockDef(String id, int world, String kind, String style, String drop) {}

	public record MobDef(String id, int world, float hp, float damage, String behavior, float scale, float width, float height,
						 String drop, String rareDrop, boolean elite, boolean nesting, boolean flying, boolean aquatic,
						 java.util.List<AttackDef> attacks) {}

	/** A creature's signature attack, generated from tools/attacks.py. Effects are "id:ticks:level" lists, gauges "name:delta". */
	public record AttackDef(String id, String kind, float mult, float radius, int hits, int interval, float knock, float lift,
							int hit, int end, int cooldown, float min, float max, int hold, int duration, int fire, float heal,
							int count, String summon, String effects, String gauges, String self, String particle, String sound) {}

	public record BossDef(String id, int world, float hp, float damage, float scale, float width, float height, String core,
						  float[] phases, boolean flying, boolean aquatic, String meet, String offering) {
		/** True for a boss that sleeps in its lair (woken by the lair heart) rather than at the arena altar. */
		public boolean lair() {
			return "lair".equals(meet);
		}
	}

	public record NpcDef(String id, int world) {}

	public record StructureDef(String id, int world, String role, String size, String rarity, String archetype) {}

	public record QuestDef(String id, int world, String type, String objKind, String objTarget, int objCount,
						   String rewardKind, String rewardTarget, int rewardCount) {}

	public record AchDef(String id, int world, String type, String trigger, String arg) {}

	/** Soul value per rarity, from the design document. */
	public static int soulValue(String rarity) {
		return switch (rarity) {
			case "common" -> 1;
			case "rare" -> 10;
			case "epic" -> 30;
			case "legendary" -> 100;
			default -> 0;
		};
	}

	/** Player gear table: weapon damage, armor total, toughness, bonus hp. */
	public static final float[][] GEAR = {
		{0, 0, 0, 0},
		{7, 16, 1, 0}, {9, 17, 2, 0}, {11, 18, 3, 2}, {13, 19, 4, 4}, {16, 20, 6, 6},
		{19, 22, 8, 8}, {23, 24, 10, 12}, {28, 26, 12, 16}, {33, 28, 14, 20}, {40, 30, 16, 24}
	};

	public static float hpMultiplier(int world) {
		return world <= 0 ? 1f : (float) Math.pow(1.35, world - 1);
	}

	public static float damageMultiplier(int world) {
		return world <= 0 ? 1f : (float) Math.pow(1.20, world - 1);
	}

	public static float speedMultiplier(int world) {
		return world <= 0 ? 1f : 1f + 0.06f * (world - 1);
	}

	public static float bossHealthPlayers(int players) {
		return 1f + 0.6f * (Math.max(1, players) - 1);
	}

	/** Attack speed of a boss fought by this many players: 1 + 0.05 x (players - 1). */
	public static float bossAttackSpeedPlayers(int players) {
		return 1f + 0.05f * (Math.max(1, players) - 1);
	}

	/** Telegraph and opening windows, in ticks, per tier. */
	public static int telegraphTicks(int world) {
		if (world <= 3) return 30;
		if (world <= 6) return 20;
		if (world <= 9) return 15;
		return 12;
	}

	public static int openingTicks(int world) {
		if (world <= 3) return 60;
		if (world <= 6) return 50;
		if (world <= 9) return 40;
		return 30;
	}
}
