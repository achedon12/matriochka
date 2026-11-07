#!/usr/bin/env bash
# Starts the mod on a dedicated server (no client), generates a chunk in every world, then stops.
# Fails on a crash, on a client class loaded on the server, on a data file that does not load, or on a world that
# does not generate.   tools/server_smoke.sh [26.2]   (the Minecraft version, 26.3 by default)
set -u
cd "$(dirname "$0")/.."
MC=${1:-26.3}
RUN=run/server
mkdir -p "$RUN"
echo "eula=true" > "$RUN/eula.txt"
cat > "$RUN/server.properties" <<P
online-mode=false
level-seed=matriochka
level-name=smoke-$MC
spawn-protection=0
view-distance=4
simulation-distance=4
P
rm -rf "$RUN/smoke-$MC"
LOG=$(mktemp)
FIFO=$(mktemp -u); mkfifo "$FIFO"
exec 3<>"$FIFO"
./gradlew runServer -Pmc="$MC" --console=plain <"$FIFO" >"$LOG" 2>&1 &
PID=$!
send() { echo "$1" >&3; }
deadline=$((SECONDS + 900))
until grep -q "Done (" "$LOG"; do
  if ! kill -0 $PID 2>/dev/null || [ $SECONDS -gt $deadline ]; then echo "the server did not start"; tail -40 "$LOG"; exit 1; fi
  sleep 2
done
for w in world_1 world_2 world_3 world_4 world_5 world_6 world_7 world_8 world_9 world_10 world_zero refuge; do
  send "execute in matriochka:$w run forceload add 0 0 32 32"
done
send "say smoke-generated"
until grep -q "smoke-generated" "$LOG"; do
  if ! kill -0 $PID 2>/dev/null || [ $SECONDS -gt $deadline ]; then echo "the server died while generating"; tail -40 "$LOG"; exit 1; fi
  sleep 2
done
sleep 10
send "stop"
wait $PID
exec 3>&-; rm -f "$FIFO"
BAD=$(grep -E "Exception generating|Missing element|Couldn't parse|Failed to load datapacks|NoClassDefFoundError|ClassNotFoundException|Mixin apply failed|Unknown dimension|Encountered an unexpected exception|crash report" "$LOG" | head -20)
if [ -n "$BAD" ]; then echo "dedicated server $MC: errors"; echo "$BAD"; exit 1; fi
echo "dedicated server $MC: ok, every world generated"
