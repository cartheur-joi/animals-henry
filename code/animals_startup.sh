#!/bin/sh

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/animalsHenry.pid"
LOG_FILE="$SCRIPT_DIR/animalsHenry.log"

sleep 15
/usr/bin/python "$SCRIPT_DIR/animalsHenry.py" >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
