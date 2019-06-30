#!/usr/bin/env python3
# -*- coding: utf-8

"""
Test movement-based exploration by sending UDP packets for commands.

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
"""

from explore import TextPrompter, get_data, main
from exploremovement import AudioExplorer, MotionPrompter
from struct import pack_into
import socket
import sys

class MotionTester:

    "A control mechanism simulating motion sensors."

    def __init__(self):
        self.init_socket()
        self.buffer = bytearray(1024)

        # Send initial values.

        self.send_values(0, 0, 0, 0)

    def init_socket(self):

        "Make a UDP socket for communication."

        # If gethostbyname throws an error, comment out that line and use the one
        # below instead.

        #UDP_IP = "put your IP address here"

        UDP_IP = socket.gethostbyname(socket.gethostname())
        UDP_PORT = 6000

        print("\nSender IP: ", UDP_IP)
        print("Port: ", UDP_PORT)

        # Create an Internet addressable UDP socket.

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((UDP_IP, UDP_PORT))

    def send_values(self, ax, ay, az, gyroY):

        "Send measurement values."

        pack_into("!f", self.buffer, 0, ax)
        pack_into("!f", self.buffer, 4, ay)
        pack_into("!f", self.buffer, 8, az)
        pack_into("!f", self.buffer, 28, gyroY)
        data = self.sock.send(self.buffer)

    # Explorer methods.

    def show_fragment(self):
        pass

    def show_fragments(self):
        pass

    def show_viewed_fragment(self):
        pass

    def select_fragment(self, identifier):
        pass

    def select_random_fragment(self):
        pass

    def forward(self):
        self.send_values(1.1, 0, 0, 0)
        self.send_values(0, 0, 0, 0)

    def rotate(self, direction):
        self.send_values(0, 0, 0, 40.1 * -direction)
        self.send_values(0, 0, 0, 0)

    def stop(self):
        pass

class RestrictedTextPrompter(TextPrompter):

    "A restricted version of the text prompter."

    def backtrack(self):
        pass

    def jump(self):
        pass

    def show_visited(self):
        pass

    def wait(self):
        print("Which way?", file=self.out)
        print("(l)eft, (r)ight, (f)orward, (q)uit", file=self.out)
        self.command = self.get_input("> ")

    def welcome(self):
        pass

if __name__ == "__main__":

    # Initialise the interaction objects.

    out = sys.stdout

    if sys.argv[1:] and sys.argv[1] == "--server":
        del sys.argv[1]

        datadir = get_data()
        explorer = AudioExplorer(datadir, out)
        prompter = MotionPrompter(explorer, out)
    else:
        explorer = MotionTester()
        prompter = RestrictedTextPrompter(explorer, out)

    main(explorer, prompter)

# vim: tabstop=4 expandtab shiftwidth=4
