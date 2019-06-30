#!/usr/bin/env python3
# -*- coding: utf-8

"""
Explore the generated data.

Copyright (C) 2018, 2019 University of Oslo

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.

----

Audio playback needs ffmpeg to play audio and pydub to be installed:

python3 -m pip install pydub

To install ffmpeg you can run "brew install ffmpeg" in the terminal on Mac OS X.
"""

from collections import deque
from explore import Explorer, Prompter, get_data, main
from math import fsum
from os.path import join
from struct import unpack_from
import select
import socket
import sys

# Audio playback.

from pydub import AudioSegment
from pydub.playback import play

class AudioExplorer(Explorer):

    "An explorer of the generated data."

    # Path to audio file.

    audiopath = "AudiosMemento"

    def play_fragment(self, identifier):

        "Play the audio for the fragment having the given 'identifier'."

        # Obtain the filename and timing details from the identifier.

        split = identifier.split(":")
        filename = split[0]
        duration = split[1].split("-")

        start = float(duration[0])
        end = float(duration[1])

        playfile = join(self.audiopath, filename + ".wav")
        sound = AudioSegment.from_file(playfile, format="wav")

        # Convert from seconds to milliseconds.

        splice = sound[start*1000:end*1000]
        play(splice)

    def play_visited(self):

        "Play audio to indicate a visited fragment."

        playfile = join(self.audiopath, "ExcerptBrunaSoplo.wav")
        sound = AudioSegment.from_file(playfile, format="wav")
        play(sound)

    def show_fragment(self, identifier=None, view=False):

        """
        Show the given fragment details for the given 'identifier' or those of
        the current fragment.
        """

        identifier = identifier or self.fragment.identifier

        # If visited, play a special sound and choose another fragment.

        if not view and identifier in self.visited:
            #self.play_visited()
            self.select_random_fragment() 

        self.play_fragment(identifier)

        # Remember this fragment as having been visited.

        if not view:
            self.visited.append(identifier)

    def show_similarity(self, fragment):
        pass

class MotionPrompter(Prompter):

    "A control mechanism employing motion sensors."

    def __init__(self, explorer, out):
        self.explorer = explorer
        self.out = out
        self.init_socket()

        # Set the first values to use in derivation.

        self.stack = deque(maxlen = 50)
        self.prev = self.receive_values()
        self.command = None

    def empty_socket(self):

        "Remove data from the socket buffer."

        input = [self.sock]
        while 1:
            inputready, o, e = select.select(input,[],[], 0.0)
            if not inputready: break
            for s in inputready: s.recv(1)

    def init_socket(self):

        "Make a UDP socket for communication."

        # If gethostbyname throws an error, comment out that line and use the one
        # below instead.

        #UDP_IP = "put your IP address here"

        UDP_IP = socket.gethostbyname(socket.gethostname())
        UDP_PORT = 6000

        print("\nReceiver IP: ", UDP_IP, file=self.out)
        print("Port: ", UDP_PORT, file=self.out)

        # Create an Internet addressable UDP socket.

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))

    def receive_values(self):

        "Receive measurement values."

        data = self.sock.recv(1024)
        ax = float("%1.4f" % unpack_from('!f', data, 0))
        ay = float("%1.4f" % unpack_from('!f', data, 4))
        az = float("%1.4f" % unpack_from('!f', data, 8))
        gyroY = float("%1.4f" % unpack_from('!f', data, 28))

        self.stack.append(gyroY)
        return ax + ay + az

    def wait(self):

        "Wait for a command."

        # Empty the socket so we do not compare data we got before audio
        # playback and data received after.

        self.empty_socket()

        # Loop, performing movements according to data from SensorUDP app.

        self.command = None

        while not self.command:
            accel_sum = self.receive_values()
            gyro_sum = fsum(self.stack)

            # The absolute value of the derivative to get jerk/rate of change in
            # acceleration.

            if abs(accel_sum - self.prev) > 1:
                print("step")
                self.command = "forward"
                self.prev = self.receive_values()

            # Check the sum of the stack of gyro values is above or below a
            # certain threshold.

            elif gyro_sum > 40:
                print("rotation left")
                self.command = "left"
                self.stack.clear()
                self.prev = self.receive_values()

            elif gyro_sum < -40:
                print("rotation right")
                self.command = "right"
                self.stack.clear()
                self.prev = self.receive_values()
            else:
                self.prev = accel_sum

    def welcome(self):

        "Choose a fragment to begin with."

        print("""
(0) If you do not have the "SensorUDP" app, download it from the "Play Store".

(1) Turn on "Acceleration" and "Rotation" in the SensorUDP app and "SEND DATA"
    to the IP and Port shown above. The computer and the mobile phone has
    to be connected to the same WiFi network.

(2) Then select a fragment to start or press Enter/Return for a random fragment.

(3) To quit, press "CONTROL + C".
""")

        self.explorer.show_fragments()
        self.jump()

if __name__ == "__main__":

    # Initialise the interaction objects.

    datadir = get_data()
    out = sys.stdout
    explorer = AudioExplorer(datadir, out)
    prompter = MotionPrompter(explorer, out)
    
    main(explorer, prompter)

# vim: tabstop=4 expandtab shiftwidth=4
