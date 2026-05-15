#!/usr/bin/env python
#
# Animals Henry by cartheur 2019
#

import alsaaudio as aa
import audioop
from time import sleep
import struct
import math
import array
import numpy as np
import wave
import os
import subprocess

class AudioPlayer:
    def __init__(self):
        self.outputGain = 4.0
        self.maxOutputGain = 16.0
        self.targetPeak = 28000.0
        self.configureMixer()
        self.prevAudiovalue = 0
        self.mouthValue = 0

    def configureMixer(self):
        self.runMixerCommand('amixer -q sset Master 100% unmute')
        self.runMixerCommand('amixer -q sset PCM 100% unmute')
        self.runMixerCommand('amixer -q sset Speaker 100% unmute')
        self.runMixerCommand('amixer -q sset Headphone 100% unmute')
        self.runMixerCommand('amixer -q sset Digital 100% unmute')
        self.runMixerCommand('amixer cset numid=1 100%') # Set PA mixer volume to 100%
        self.runMixerCommand('amixer cset numid=2 2') # Set right mixer to be "right" (2)
        self.runMixerCommand('amixer cset numid=3 1') # Set left mixer to be "left" (1)
        self.runMixerCommand('amixer cset numid=4 1') # Set DAC self.output to be "Direct" (2... or 1 for "Mixed" if you prefer)

    def runMixerCommand(self, command):
        subprocess.call(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    def play(self,fileName):
        # Initialise matrix
        matrix=[0,0,0,0,0,0,0,0]

        # Set up audio
        wavfile = wave.open(fileName,'r')
        chunk = 1024
        output = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
        output.setchannels(2)
        output.setrate(22050)
        output.setformat(aa.PCM_FORMAT_S16_LE)
        output.setperiodsize(chunk)

        data = wavfile.readframes(chunk)
        try:
          while data!='':
             peak = audioop.max(data, 2)
             gain = self.outputGain
             if peak > 0:
                gain = max(gain, min(self.maxOutputGain, self.targetPeak / float(peak)))

             boostedData = audioop.mul(data, 2, gain)
             stereoData = audioop.tostereo(boostedData, 2, 1.0, 1.0)
             output.write(stereoData)
             # Split channel data and find maximum volume   
             channel_l=audioop.tomono(stereoData, 2, 1.0, 0.0)
             channel_r=audioop.tomono(stereoData, 2, 0.0, 1.0)
             max_vol_factor =5000
             max_l = audioop.max(channel_l,2)/max_vol_factor
             max_r = audioop.max(channel_r,2)/max_vol_factor

             for i in range (1,8):
                self.generateMouthSignal((1<<max_r)-1)
                
             data = wavfile.readframes(chunk)
        except:
          data = None
        
        os.system( '/etc/init.d/alsa-utils restart' )
        self.configureMixer()
        sleep( .25 )

    def generateMouthSignal(self,val):
        delta = val - self.prevAudiovalue 
        if( delta < -2 or val == 0 ):
            self.mouthValue = 0
        elif( delta > 0 ):
            self.mouthValue = 1

        self.prevAudiovalue = val
