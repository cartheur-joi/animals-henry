#!/bin/sh

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/animalsHenry.pid"
PROCESS_PATTERN="$SCRIPT_DIR/animalsHenry.py"
CLOSE_DELAY=2

find_pid() {
    if [ -f "$PID_FILE" ]; then
        PID="$(cat "$PID_FILE" 2>/dev/null)"
        if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
            echo "$PID"
            return 0
        fi
    fi

    pgrep -f "$PROCESS_PATTERN" | head -n 1
}

PID="$(find_pid)"

if [ -n "$PID" ]; then
    kill -TERM "$PID" 2>/dev/null || true
    sleep "$CLOSE_DELAY"
fi

exec sudo reboot
