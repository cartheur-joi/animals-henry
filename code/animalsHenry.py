#!/usr/bin/python
# July 2021
# Animals Henry (bear) by m.e. of cartheur
# Idea incubated 27.01.2015 and now has a manifestation!
# This script is for utilization of two motors: eyes and nose-mouth.

# DEPENDENCIES
# apt-get install python-setuptools python-dev build-essential espeak alsa-utils
# apt-get install python-alsaaudio python-numpy python-twitter python-bottle mplayer

import sys
import time
import subprocess
import os
import signal
from random import randint
from threading import Thread, Event
from animalsHenry_audioPlayer import AudioPlayer
from animalsHenry_gpio import GPIO
from animalsHenry_webFramework import WebFramework

fullMsg = ""

EYES_OPEN = 1017 # GPIO pin assigned to open the eyes. XIO-P4
EYES_CLOSE = 1019 # GPIO pin assigned to close the eyes. XIO-P6
MOUTH_OPEN = 1018 # GPIO pin assigned to open the mouth. XIO-P5
MOUTH_CLOSE = 1020 # GPIO pin assigned to close the mouth. XIO-P7
EYE_DRIVE_TIME = 0.25
MOUTH_DRIVE_TIME = 0.15

# Establish a connection to the GPIO pins.
io = GPIO()
io.setup( MOUTH_OPEN )
io.setup( EYES_OPEN )
io.setup( MOUTH_CLOSE )
io.setup( EYES_CLOSE )

audio = None
isRunning = True
shutdownEvent = Event()
shutdownInProgress = False
speechFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "speech_runtime.wav")

def waitOrShutdown(seconds):
    shutdownEvent.wait(seconds)
    return shutdownEvent.is_set()

def closeEyesForShutdown():
    io.set( EYES_OPEN, 0 )
    io.set( EYES_CLOSE, 1 )
    io.set( MOUTH_OPEN, 0 )
    io.set( MOUTH_CLOSE, 0 )

def stopEyes():
    io.set( EYES_OPEN, 0 )
    io.set( EYES_CLOSE, 0 )

def driveEyes(action):
    if action == "open":
        io.set( EYES_CLOSE, 0 )
        io.set( EYES_OPEN, 1 )
    elif action == "close":
        io.set( EYES_OPEN, 0 )
        io.set( EYES_CLOSE, 1 )
    else:
        stopEyes()

    if action != "stop":
        if waitOrShutdown( EYE_DRIVE_TIME ):
            return True
        stopEyes()

    return shutdownEvent.is_set()

def stopMouth():
    io.set( MOUTH_OPEN, 0 )
    io.set( MOUTH_CLOSE, 0 )

def requestShutdown(signum=None, frame=None):
    global isRunning
    global shutdownInProgress

    shutdownInProgress = True
    isRunning = False
    shutdownEvent.set()
    closeEyesForShutdown()

# Set the mouth in motion to approximate visual pronunciation of audio.
def updateMouth():
    lastMouthEvent = 0
    lastMouthDriveTime = 0

    while( audio == None ):
        if waitOrShutdown( 0.1 ):
            return
        
    while isRunning:
        if( audio.mouthValue != lastMouthEvent ):
            lastMouthEvent = audio.mouthValue
            lastMouthDriveTime = time.time()

            if( audio.mouthValue == 1 ):
                io.set( MOUTH_OPEN, 1 )
                io.set( MOUTH_CLOSE, 0 )
            else:
                io.set( MOUTH_OPEN, 0 )
                io.set( MOUTH_CLOSE, 1 )
        else:
            if( lastMouthDriveTime > 0 and time.time() - lastMouthDriveTime > MOUTH_DRIVE_TIME ):
                stopMouth()

        time.sleep( 0.02 )

    stopMouth()

# A routine for blinking the eyes in a semi-random fashion.
def updateEyes():
    while isRunning:
        if driveEyes( "close" ):
            break
        if waitOrShutdown( 3.0 ):
            break
        if driveEyes( "open" ):
            break
        if waitOrShutdown( 0.4 ):
            break
        if driveEyes( "close" ):
            break
        if waitOrShutdown( 3.5 ):
            break
        stopEyes()
        if waitOrShutdown( randint( 0,7) ):
            break

    if shutdownInProgress:
        closeEyesForShutdown()
    else:
        stopEyes()
   
def talk(myText):
    speechText = str(myText or "")

    try:
        generator = subprocess.Popen(
            ["text2wave", "-o", speechFile],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        generator.communicate(speechText)

        if generator.returncode == 0 and os.path.isfile(speechFile):
            audio.play(speechFile)
        else:
            fallback = subprocess.Popen(
                ["festival", "--tts"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            fallback.communicate(speechText)
    finally:
        if os.path.isfile(speechFile):
            os.remove(speechFile)

    return myText

signal.signal( signal.SIGTERM, requestShutdown )
signal.signal( signal.SIGINT, requestShutdown )

mouthThread = Thread(target=updateMouth)
mouthThread.start()
eyesThread = Thread(target=updateEyes)
eyesThread.start()     
audio = AudioPlayer()

web = WebFramework(talk)
isRunning = False
shutdownEvent.set()
mouthThread.join( 1.0 )
eyesThread.join( 1.0 )
if not shutdownInProgress:
    io.cleanup()
sys.exit(1)
