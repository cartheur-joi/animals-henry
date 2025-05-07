#!/usr/bin/python
# September 2019
# Animals Henry (bear) by m.e. of cartheur
# Idea incubated 27.01.2015 and now has a manifestation!
# This script is for utilization of two motors, eyes and nose-mouth.

# DEPENDENCIES
# apt-get install python-setuptools python-dev build-essential espeak alsa-utils
# apt-get install python-alsaaudio python-numpy python-twitter python-bottle mplayer

import sys
import time
import subprocess
import os
from random import randint
from threading import Thread
from animalsHenry_audioPlayer import AudioPlayer
from animalsHenry_gpio import GPIO
from animalsHenry_webFramework import WebFramework

fullMsg = ""

EYES_OPEN = 1017 # GPIO pin assigned to open the eyes. XIO-P4
EYES_CLOSE = 1019 # GPIO pin assigned to close the eyes. XIO-P6
MOUTH_OPEN = 1018 # GPIO pin assigned to open the mouth. XIO-P5
MOUTH_CLOSE = 1020 # GPIO pin assigned to close the mouth. XIO-P7

# Establish a connection to the GPIO pins.
io = GPIO()
io.setup( MOUTH_OPEN )
io.setup( EYES_OPEN )
io.setup( MOUTH_CLOSE )
io.setup( EYES_CLOSE )

audio = None
isRunning = True

# Set the mouth in motion to approximate visual pronunciation of audio.
def updateMouth():
    lastMouthEvent = 0
    lastMouthEventTime = 0

    while( audio == None ):
        time.sleep( 0.1 )
        
    while isRunning:
        if( audio.mouthValue != lastMouthEvent ):
            lastMouthEvent = audio.mouthValue
            lastMouthEventTime = time.time()

            if( audio.mouthValue == 1 ):
                io.set( MOUTH_OPEN, 1 )
                io.set( MOUTH_CLOSE, 0 )
            else:
                io.set( MOUTH_OPEN, 0 )
                io.set( MOUTH_CLOSE, 1 )
        else:
            if( time.time() - lastMouthEventTime > 0.5 ):
                io.set( MOUTH_OPEN, 0 )
                io.set( MOUTH_CLOSE, 0 )

# A routine for blinking the eyes in a semi-random fashion.
def updateEyes():
    while isRunning:
        io.set( EYES_CLOSE, 1 )
        io.set( EYES_OPEN, 0 )
        time.sleep( 3.0 )
        io.set( EYES_CLOSE, 0 )
        io.set( EYES_OPEN, 1 )
        time.sleep( 0.4 )
        io.set( EYES_CLOSE, 1 )
        io.set( EYES_OPEN, 0 )
        time.sleep( 3.5 )
        io.set( EYES_CLOSE, 0 )
        io.set( EYES_OPEN, 0 )
        time.sleep( randint( 0,7) )
   
def talk(myText):
    os.system( "espeak \",...\" 2>/dev/null" ) # Sometimes the beginning of audio can get cut off. Insert silence.
    time.sleep( 0.5 )
    os.system( "espeak -w speech.wav \"" + myText + "\" -s 130" )
    audio.play("speech.wav")
    return myText

mouthThread = Thread(target=updateMouth)
mouthThread.start()
eyesThread = Thread(target=updateEyes)
eyesThread.start()     
audio = AudioPlayer()

web = WebFramework(talk)
isRunning = False
io.cleanup()
sys.exit(1)
