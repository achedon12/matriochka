package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.saveddata.SavedDataType;

/**
 * Server-wide Matriochka state: groups, their progression, their parcels and their world blocks.
 * Stored in the overworld data storage as one compound tag.
 */
public class MatrioData extends SavedData {
	public static final SavedDataType<MatrioData> TYPE = new SavedDataType<>(Matriochka.id("state"), MatrioData::new,
		CompoundTag.CODEC.xmap(MatrioData::new, d -> d.root), null);

	private final CompoundTag root;

	public MatrioData() {
		this(new CompoundTag());
	}

	private MatrioData(CompoundTag root) {
		this.root = root;
	}

	public static MatrioData get(MinecraftServer server) {
		return server.overworld().getDataStorage().computeIfAbsent(TYPE);
	}

	private CompoundTag sub(CompoundTag parent, String key) {
		if (!parent.contains(key)) parent.put(key, new CompoundTag());
		return parent.getCompoundOrEmpty(key);
	}

	// ----------------------------------------------------------- groups
	public String groupOf(UUID player) {
		CompoundTag players = sub(root, "players");
		String g = players.getStringOr(player.toString(), "");
		if (g.isEmpty()) {
			g = player.toString();
			players.putString(player.toString(), g);
			CompoundTag grp = group(g);
			grp.putString("leader", player.toString());
			ListTag members = new ListTag();
			members.add(StringTag.valueOf(player.toString()));
			grp.put("members", members);
			setDirty();
		}
		return g;
	}

	public CompoundTag group(String id) {
		return sub(sub(root, "groups"), id);
	}

	public List<UUID> members(String group) {
		List<UUID> out = new ArrayList<>();
		for (Tag t : group(group).getListOrEmpty("members")) {
			t.asString().ifPresent(s -> out.add(UUID.fromString(s)));
		}
		return out;
	}

	public boolean join(UUID player, String group) {
		CompoundTag grp = group(group);
		ListTag members = grp.getListOrEmpty("members");
		if (members.size() >= 8) return false;
		leave(player);
		members.add(StringTag.valueOf(player.toString()));
		grp.put("members", members);
		sub(root, "players").putString(player.toString(), group);
		setDirty();
		return true;
	}

	public void leave(UUID player) {
		String g = groupOf(player);
		CompoundTag grp = group(g);
		ListTag members = grp.getListOrEmpty("members");
		ListTag kept = new ListTag();
		for (Tag t : members) if (!t.asString().orElse("").equals(player.toString())) kept.add(t);
		grp.put("members", kept);
		if (grp.getStringOr("leader", "").equals(player.toString()) && !kept.isEmpty()) {
			grp.putString("leader", kept.getFirst().asString().orElse(""));
		}
		String own = player.toString();
		sub(root, "players").putString(own, own);
		CompoundTag mine = group(own);
		mine.putString("leader", own);
		ListTag m = new ListTag();
		m.add(StringTag.valueOf(own));
		mine.put("members", m);
		setDirty();
	}

	// ----------------------------------------------------------- progression (bit 0 = Block Guardian, bit n = world n boss)
	public boolean defeated(String group, int world) {
		return (group(group).getIntOr("done", 0) & (1 << world)) != 0;
	}

	public void markDefeated(String group, int world) {
		CompoundTag g = group(group);
		g.putInt("done", g.getIntOr("done", 0) | (1 << world));
		setDirty();
	}

	public int highestDefeated(String group) {
		int bits = group(group).getIntOr("done", 0);
		int best = -1;
		for (int i = 0; i <= 10; i++) if ((bits & (1 << i)) != 0) best = i;
		return best;
	}

	public boolean defeated(ServerPlayer p, int world) {
		return defeated(groupOf(p.getUUID()), world);
	}

	// ----------------------------------------------------------- parcels
	public int parcel(String group) {
		CompoundTag g = group(group);
		if (!g.contains("parcel")) {
			int next = root.getIntOr("parcel_counter", 0);
			root.putInt("parcel_counter", next + 1);
			g.putInt("parcel", next);
			setDirty();
		}
		return g.getIntOr("parcel", 0);
	}

	public CompoundTag worldEntry(String group, int world) {
		return sub(sub(group(group), "worlds"), Integer.toString(world));
	}

	public void changed() {
		setDirty();
	}

	public CompoundTag root() {
		return root;
	}
}
