#!/usr/bin/env python
#
# Simple motor test for Henry eyes and mouth.
#

import sys
import time
from animalsHenry_gpio import GPIO

EYES_OPEN = 1017
EYES_CLOSE = 1019
MOUTH_OPEN = 1018
MOUTH_CLOSE = 1020


def set_outputs(io, open_pin, close_pin, action):
    if action == "open":
        io.set(open_pin, 1)
        io.set(close_pin, 0)
    elif action == "close":
        io.set(open_pin, 0)
        io.set(close_pin, 1)
    else:
        io.set(open_pin, 0)
        io.set(close_pin, 0)


def pulse(io, name, open_pin, close_pin, action, seconds):
    print("%s %s for %.1f seconds" % (name, action, seconds))
    set_outputs(io, open_pin, close_pin, action)
    time.sleep(seconds)
    set_outputs(io, open_pin, close_pin, "stop")
    time.sleep(0.5)


def main():
    io = GPIO()
    io.setup(MOUTH_OPEN)
    io.setup(EYES_OPEN)
    io.setup(MOUTH_CLOSE)
    io.setup(EYES_CLOSE)

    try:
        print("Testing eyes")
        pulse(io, "eyes", EYES_OPEN, EYES_CLOSE, "close", 2.0)
        pulse(io, "eyes", EYES_OPEN, EYES_CLOSE, "open", 2.0)

        print("Testing mouth")
        pulse(io, "mouth", MOUTH_OPEN, MOUTH_CLOSE, "open", 1.5)
        pulse(io, "mouth", MOUTH_OPEN, MOUTH_CLOSE, "close", 1.5)

        print("Testing combined motion")
        set_outputs(io, EYES_OPEN, EYES_CLOSE, "close")
        set_outputs(io, MOUTH_OPEN, MOUTH_CLOSE, "open")
        time.sleep(1.5)
        set_outputs(io, EYES_OPEN, EYES_CLOSE, "open")
        set_outputs(io, MOUTH_OPEN, MOUTH_CLOSE, "close")
        time.sleep(1.5)
        set_outputs(io, EYES_OPEN, EYES_CLOSE, "stop")
        set_outputs(io, MOUTH_OPEN, MOUTH_CLOSE, "stop")
        print("Motor test complete")
    finally:
        io.cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())
