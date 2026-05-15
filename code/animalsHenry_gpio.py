#!/usr/bin/env python
#
# Animals Henry by cartheur 2019
# This sets the state of various GPIO pins
#

import os
import time
import subprocess
from threading import Thread

class GPIO:
    def __init__(self):
        self.pins = []
        
    def setup(self,pin):
        cmd = "echo " + str(pin) + " > /sys/class/gpio/export"
        subprocess.call(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        gpioPath = "/sys/class/gpio/gpio" + str(pin)
        waitCount = 0
        while not os.path.isdir(gpioPath) and waitCount < 20:
            time.sleep(0.05)
            waitCount += 1

        cmd = "echo \"out\" > " + gpioPath + "/direction"
        subprocess.call(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.pins.append([pin,0,0])
        self.set( pin, 0 )
        
    def set(self,pin, val):
        if ( self.pins != None ):
            for pinObject in self.pins:
                if(pinObject[0]==pin and pinObject[1]!=val):
                    pinObject[1]=val
                    cmd = "echo " + str(val) + " > /sys/class/gpio/gpio" + str(pinObject[0]) + "/value"
                    subprocess.call(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    def cleanup(self):
        if self.pins != None:
            for pinObject in self.pins:
                cmd = "echo 0 > /sys/class/gpio/gpio" + str(pinObject[0]) + "/value"
                subprocess.call(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.pins = None
