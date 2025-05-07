#!/usr/bin/env python
#
# Animals Henry by cartheur 2019
#

from bottle import run, get, post, request, route, redirect
import socket

class WebFramework:
    def __init__(self,func):
        self.ip = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        print( "--------------------------------" )
        print( "cartheur presents emotional toys" )
        print( "-----" )
        print( "Animals Henry - The Friendly Bear" )
        print( "Designed, written, and programmed by m.e." )
        print( "-----" )
        print( "Copyright 2021 Cartheur, all rights reserved" )
        print( "Copyright 2000 - 2007 Paradox Technologies" )
        print( "Copyright 2008 - 2021 Cartheur Robotics, spol. s r.o." )
        print( "-------" )
        print( "Open a browser with the address: " + str(self.ip) + ":8080 to talk to your animal" )
        print( "Else, access this script from your favourite API" )
        print( "A serious application of Boagaphish threading back to the Summer of 1987" )
        print( "-------------------------------" )
        self.talkFunc = func
        
        @route('/')
        def index():
            return '''
                <form action="/" method="post">
                    What do you want your animal to say?<p><input name="speech" type="text" />
                    <input value="GO" type="submit" />
                </form>
            '''
        @post('/')
        def speak():
            speech = request.forms.get('speech')            
            self.talkFunc( speech )
            redirect('/')

        run(host=self.ip, port=8080, debug=True)
