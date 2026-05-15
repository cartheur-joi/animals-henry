#!/usr/bin/env python
#
# Simple motor test for Henry eyes and mouth.
#

import os
import signal
import subprocess
import sys
import time
from threading import Event
from threading import Thread

from animalsHenry_audioPlayer import AudioPlayer
from animalsHenry_gpio import GPIO

EYES_OPEN = 1017
EYES_CLOSE = 1019
MOUTH_OPEN = 1018
MOUTH_CLOSE = 1020
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SPEECH_FILE = os.path.join(SCRIPT_DIR, "speech.wav")


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


def find_henry_pid():
    try:
        output = subprocess.Popen(
            "pgrep -f '/animalsHenry.py$'",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()[0]
    except:
        return None

    if not output:
        return None

    pid_text = output.splitlines()[0].strip()
    if not pid_text:
        return None

    try:
        return int(pid_text)
    except:
        return None


def pause_henry():
    pid = find_henry_pid()
    if pid == None:
        return None

    try:
        os.kill(pid, signal.SIGSTOP)
        print("Paused animalsHenry.py (pid %s)" % pid)
        time.sleep(0.5)
        return pid
    except:
        return None


def resume_henry(pid):
    if pid == None:
        return

    try:
        os.kill(pid, signal.SIGCONT)
        print("Resumed animalsHenry.py (pid %s)" % pid)
    except:
        pass


def update_mouth(io, audio, stop_event):
    last_mouth_event = 0
    last_mouth_event_time = time.time()

    while not stop_event.is_set():
        if audio.mouthValue != last_mouth_event:
            last_mouth_event = audio.mouthValue
            last_mouth_event_time = time.time()

            if audio.mouthValue == 1:
                io.set(MOUTH_OPEN, 1)
                io.set(MOUTH_CLOSE, 0)
            else:
                io.set(MOUTH_OPEN, 0)
                io.set(MOUTH_CLOSE, 1)
        else:
            if time.time() - last_mouth_event_time > 0.5:
                io.set(MOUTH_OPEN, 0)
                io.set(MOUTH_CLOSE, 0)

        time.sleep(0.02)

    io.set(MOUTH_OPEN, 0)
    io.set(MOUTH_CLOSE, 0)


def play_speech_with_mouth(io):
    if not os.path.isfile(SPEECH_FILE):
        print("speech.wav not found at %s" % SPEECH_FILE)
        return

    print("Playing speech.wav with mouth movement")
    audio = AudioPlayer()
    stop_event = Event()
    mouth_thread = Thread(target=update_mouth, args=(io, audio, stop_event))
    mouth_thread.start()

    try:
        audio.play(SPEECH_FILE)
        time.sleep(0.5)
    finally:
        stop_event.set()
        mouth_thread.join(1.0)


def main():
    paused_pid = pause_henry()
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

        play_speech_with_mouth(io)
        print("Motor test complete")
    finally:
        io.cleanup()
        resume_henry(paused_pid)

    return 0


if __name__ == "__main__":
    sys.exit(main())
