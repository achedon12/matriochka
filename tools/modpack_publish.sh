#!/usr/bin/env bash
# Uploads the Matriochka Pack built by tools/modpack.py to its own Modrinth or CurseForge project.
#
#   tools/modpack_publish.sh modrinth      # build/modpack/*.mrpack, one version per flavour
#   tools/modpack_publish.sh curseforge    # build/modpack/*-curseforge.zip, one file per flavour
#
# Environment:
#   TOKEN     MODRINTH_TOKEN or CURSEFORGE_TOKEN (upload token of the owner)
#   PROJECT   the pack's project id (MODRINTH_PACK_PROJECT_ID / CURSEFORGE_PACK_PROJECT_ID variable)
#   VERSION   mod version (0.4.0), MC  the default Minecraft version (26.3)
#   MCS       every Minecraft version with a pack (default: MC alone); the default's pack keeps the plain version
#             number (0.7.0, 0.7.0-hard) and is uploaded last, the others get +<mc> (0.7.0+26.2, 0.7.0-hard+26.2)
#   NOTES     file with the "## <version>" section of CHANGELOG.md (default: notes.md)
#   PACK_DIR  folder of the pack files (default: build/modpack)
#   DRY_RUN   1: print each request instead of uploading (reads still happen)
#
# Without TOKEN or PROJECT it prints a ::warning:: and exits 0. The hard pack is uploaded first, so that the normal
# pack is the newest version, the one launchers install by default.
set -euo pipefail

target=${1:?usage: modpack_publish.sh modrinth|curseforge}
: "${VERSION:?VERSION is not set}" "${MC:?MC is not set}"
NOTES=${NOTES:-notes.md}
PACK_DIR=${PACK_DIR:-build/modpack}
DRY_RUN=${DRY_RUN:-0}
MCS=${MCS:-$MC}
# the other versions first, the default last: its normal pack ends up the newest version, the one launchers pick
ORDER="$(for m in $MCS; do [ "$m" = "$MC" ] || echo "$m"; done | tr '\n' ' ') $MC"
UA="achedon12/matriochka release workflow"

changelog() {
	echo "Matriochka Pack for Matriochka $VERSION (Minecraft ${PMC:-$MC}, Fabric). The pack's mod list is on the project page; what changed in the mod:"
	echo
	if [ -s "$NOTES" ]; then cat "$NOTES"; else echo "See https://github.com/achedon12/matriochka/releases/tag/v$VERSION"; fi
}

modrinth() {
	if [ -z "${TOKEN:-}" ] || [ -z "${PROJECT:-}" ]; then
		echo "::warning::The Modrinth modpack project is not configured (MODRINTH_TOKEN secret / MODRINTH_PACK_PROJECT_ID variable), skipping"
		return 0
	fi
	api=https://api.modrinth.com/v2
	code=$(curl -sS -o mr-versions.json -w '%{http_code}' -H "Authorization: $TOKEN" -H "User-Agent: $UA" "$api/project/$PROJECT/version")
	if [ "$code" = 404 ] && [ "$DRY_RUN" = 1 ]; then
		echo "dry run: Modrinth has no project $PROJECT (HTTP 404), going on with no existing version"
		echo '[]' > mr-versions.json
	elif [ "$code" != 200 ]; then
		echo "::error::Modrinth answered HTTP $code for project $PROJECT: $(head -c 300 mr-versions.json)"
		return 1
	fi
	for PMC in $ORDER; do
	notes=$(changelog)
	for suffix in -hard ""; do
		number="$VERSION$suffix"
		[ "$PMC" = "$MC" ] || number="$number+$PMC"
		file="$PACK_DIR/matriochka-pack-$VERSION$suffix+$PMC.mrpack"
		name="Matriochka Pack $VERSION"
		[ "$PMC" = "$MC" ] || name="$name for $PMC"
		[ -n "$suffix" ] && name="$name (Hard)"
		featured=false; [ "$PMC" = "$MC" ] && featured=true
		if [ ! -f "$file" ]; then
			echo "::error::$file is missing (run tools/modpack.py first)"
			return 1
		fi
		if jq -e --arg n "$number" 'any(.[]; .version_number == $n)' mr-versions.json >/dev/null; then
			echo "Modrinth already has version $number, skipping"
			continue
		fi
		data=$(jq -n \
			--arg project "$PROJECT" --arg name "$name" --arg number "$number" --arg mc "$PMC" --arg changelog "$notes" --argjson featured "$featured" \
			'{project_id: $project, name: $name, version_number: $number, changelog: $changelog,
			  game_versions: [$mc], loaders: ["fabric"], version_type: "beta", featured: $featured, environment: "client_only_server_optional",
			  dependencies: [], file_parts: ["file"], primary_file: "file"}')
		if [ "$DRY_RUN" = 1 ]; then
			echo "dry run: POST $api/version with $(basename "$file") ($(stat -c %s "$file") bytes)"
			echo "$data" | jq 'del(.changelog)'
			continue
		fi
		curl -sS --fail-with-body -H "Authorization: $TOKEN" -H "User-Agent: $UA" \
			--form-string "data=$data" -F "file=@$file;type=application/x-modrinth-modpack+zip" \
			"$api/version" -o mr-upload.json
		echo "Modrinth: version $number uploaded ($(jq -r .id mr-upload.json))"
	done
	done
}

curseforge() {
	if [ -z "${TOKEN:-}" ] || [ -z "${PROJECT:-}" ]; then
		echo "::warning::The CurseForge modpack project is not configured (CURSEFORGE_TOKEN secret / CURSEFORGE_PACK_PROJECT_ID variable), skipping"
		return 0
	fi
	api=https://minecraft.curseforge.com/api
	# a modpack file is tagged with its Minecraft version only: the loader comes from its manifest.json
	for PMC in $ORDER; do
	mcslug="minecraft-$(echo "$PMC" | cut -d. -f1-2 | tr . -)"
	if curl -fsS -H "X-Api-Token: $TOKEN" "$api/game/version-types" -o cf-types.json 2>/dev/null &&
		curl -fsS -H "X-Api-Token: $TOKEN" "$api/game/versions" -o cf-versions.json 2>/dev/null; then
		ids=$(jq -nc --slurpfile t cf-types.json --slurpfile v cf-versions.json --arg mc "$PMC" --arg mcslug "$mcslug" '
			[$t[0][] | select(.slug == $mcslug) | .id][0] as $type
			| [$v[0][] | select(.gameVersionTypeID == $type and .name == $mc) | .id] | unique')
	elif [ "$DRY_RUN" = 1 ]; then
		echo "dry run: the CurseForge game versions need a valid token, using a placeholder id"
		ids='[0]'
	else
		echo "::error::cannot read the CurseForge game versions (is CURSEFORGE_TOKEN valid?)"
		return 1
	fi
	if [ "$ids" = "[]" ]; then
		echo "::error::CurseForge has no game version $PMC"
		return 1
	fi
	echo "CurseForge game version ids: $ids"
	notes=$(changelog)
	for suffix in -hard ""; do
		file="$PACK_DIR/matriochka-pack-$VERSION$suffix+$PMC-curseforge.zip"
		name="Matriochka Pack $VERSION"
		[ "$PMC" = "$MC" ] || name="$name for $PMC"
		[ -n "$suffix" ] && name="$name (Hard)"
		if [ ! -f "$file" ]; then
			echo "::error::$file is missing (run tools/modpack.py --curseforge first)"
			return 1
		fi
		metadata=$(jq -n --arg changelog "$notes" --arg name "$name" --argjson versions "$ids" \
			'{changelog: $changelog, changelogType: "markdown", displayName: $name, releaseType: "beta", gameVersions: $versions}')
		if [ "$DRY_RUN" = 1 ]; then
			echo "dry run: POST $api/projects/$PROJECT/upload-file with $(basename "$file") ($(stat -c %s "$file") bytes)"
			echo "$metadata" | jq 'del(.changelog)'
			continue
		fi
		curl -sS --fail-with-body -H "X-Api-Token: $TOKEN" \
			--form-string "metadata=$metadata" -F "file=@$file" \
			"$api/projects/$PROJECT/upload-file" -o cf-upload.json
		echo "CurseForge: $name uploaded (file $(jq -r .id cf-upload.json))"
	done
	done
}

case "$target" in
	modrinth) modrinth ;;
	curseforge) curseforge ;;
	*) echo "usage: modpack_publish.sh modrinth|curseforge" >&2; exit 2 ;;
esac
