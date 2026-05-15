#!/bin/sh

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/animalsHenry.pid"

python "$SCRIPT_DIR/animalsHenry.py" &
echo $! > "$PID_FILE"
