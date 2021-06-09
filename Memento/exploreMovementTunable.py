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
"""

from os import listdir
from os.path import isdir, join
import codecs
import random
import sys
import math #For sum of float
import socket #UDP connection
from struct import *
import csv #Read/write csv file
from collections import deque #Stack
import select
import time

# For displaying the phone metrics
import matplotlib.pyplot as plt

#Audio playback (need ffmpeg to play audio and install pydub (python3 -m pip install pydub))
#For installing ffmpeg you can run "brew install ffmpeg" in the terminal
#For installing pydub you can run "python3 -m pip install pydub"
from pydub import AudioSegment
from pydub.playback import play

# importing the file mlExplore.py
import mlExplore as mlE

encoding = "utf-8"

#path to audiofile
audiopath = "AudiosMemento/"

def readfile(filename):

    "Return the text in 'filename'."

    f = open(filename, encoding=encoding)
    try:
        return f.read()
    finally:
        f.close()

class Explorer:

    "An explorer of the generated data."

    def __init__(self, datadir, out):

        "Initialise the explorer with the 'datadir' and 'out' stream."
        
        self.datadir = datadir
        self.out = out

        # Maintain a current fragment and step forward across related fragments.

        self.fragment = None
        self.step = None
        self.left_rotation = None
        self.right_rotation = None

        # Remember visited fragments.

        self.visited = []

    def have_rotation(self):
        return self.left_rotation is not None or self.right_rotation is not None

    def have_step(self):
        return self.step is not None

    # Fragment selection.

    def get_fragments(self):

        "Return all the fragment identifiers."

        return listdir(self.datadir)

    def select_fragment(self, identifier):

        "Select the fragment with the given 'identifier'."

        if identifier not in self.get_fragments():
            return

        # Reset stepping and rotation.

        self.fragment = self.open_fragment(identifier)
        self.step = None
        self.left_rotation = None
        self.right_rotation = None

    def select_random_fragment(self):

        "Select a random fragment."
        unvisited = set(self.get_fragments()).difference(self.visited)
        l = random.sample(unvisited, 1)
        if l:
            self.select_fragment(l[0])
        
        return self.fragment.identifier

    # Fragment directory contents.

    def open_fragment(self, identifier):

        "Return a fragment object for the 'identifier'."

        return Fragment(identifier, join(self.datadir, identifier))

    # Convenience methods.

    def get_rotation_fragment(self):

        "Return the identifier of the current rotation fragment."

        if self.left_rotation is not None:
            sequence = "left"
            i = self.left_rotation
        elif self.right_rotation is not None:
            sequence = "right"
            i = self.right_rotation
        else:
            return self.fragment.identifier

        related = self.fragment.get_relations(sequence)
        return related[i].get_data("fragment")

    def get_step_fragment(self):

        "Return the identifier of the current step fragment."

        if self.have_step():
            related = self.fragment.get_relations("forward")
            fragment = related[self.step]
            return fragment.get_data("fragment")
        else:
            return self.fragment.identifier

    # Output methods.

    def show_fragments(self):

        "Show all the fragment identifiers."

        identifiers = self.get_fragments()
        identifiers.sort()

        for identifier in identifiers:
            print(identifier, file=self.out)

    def show_fragment(self, identifier=None, view=False):

        """
        Show the given fragment details for the given 'identifier' or those of
        the current fragment.
        """

        fragment = identifier and self.open_fragment(identifier) or self.fragment

        if not view and fragment.identifier in self.visited:
            print("VISITED!", file=self.out)
            print(file=self.out)
            return fragment.identifier, True
        else:
            print(fragment.identifier, file=self.out)
            print(fragment.get_data("category"), file=self.out)
            print(file=self.out)
            print(fragment.get_data("text"), file=self.out)
            print(file=self.out)

        if self.step is None:
            related = fragment.get_relations("forward")
            unvisited = set(map(lambda f: f.identifier, related)).difference(self.visited)
            print("%d fragments ahead (%d unseen)." % (len(related), len(unvisited)), file=self.out)
            print(file=self.out)

        # Remember this fragment as having been visited.

        if not view:
            self.visited.append(fragment.identifier)
        
        return fragment.identifier, False

    def show_viewed_fragment(self):

        "Show the viewed fragment regardless of whether it has been visited."

        identifier = self.get_rotation_fragment() or self.get_step_fragment()

        self.show_fragment(identifier, view=True)

    def show_similarity(self, fragment):

        "Show similarity to the given related 'fragment'."

        print("Measure:", fragment.get_data("measure"), file=self.out)
        print("Similarity:", fragment.get_data("similarity"), file=self.out)
        print(file=self.out)

    # Navigation methods.

    def forward(self):

        """
        Move forward from the current fragment, showing fragment details in the
        sequence ahead. If the final fragment in the sequence is reached, it is
        selected as the current fragment.

        If a rotation fragment was being shown, it is selected as the current
        fragment and provides the sequence of related fragments.
        """

        # If rotating, select the currently-viewed fragment first.

        if self.have_rotation():
            self.select_fragment(self.get_rotation_fragment())

        # Step forward to the first or subsequent fragments. If reaching the
        # limit, select the final fragment in the sequence and step forward from
        # it.

        related = self.fragment.get_relations("forward")

        if related:
            limit = len(related) - 1

            if self.step is None:
                self.step = 0
            elif self.step < limit:
                self.step += 1
            
            print("Step #%d..." % self.step, file=self.out)
            self.show_similarity(related[self.step])

            if self.step == limit:
                self.select_fragment(self.get_step_fragment())
                self.step = None

        return self.show_fragment(self.get_step_fragment())

    def rotate(self, direction):

        """
        Rotate in the given 'direction' (negative to the left, positive to the
        right) from the current fragment, showing fragment details in the
        sequence oriented on the current fragment's category. If the end of the
        sequence is reached, the sequence will be navigated from the opposite
        end.

        If a step fragment was being shown, it is selected as the current
        fragment and provides the sequence of related fragments.
        """

        # If stepping forward, select the currently-viewed fragment first.

        if self.step is not None:
            self.select_fragment(self.get_step_fragment())

        # If changing rotation direction, select the currently-viewed fragment.

        elif self.left_rotation is not None and direction > 0 or \
             self.right_rotation is not None and direction < 0:

            self.select_fragment(self.get_rotation_fragment())

        # Choose the sequence of fragments.

        if direction < 0:
            sequence = "left"
            i = self.left_rotation
        else:
            sequence = "right"
            i = self.right_rotation

        # Cycle through the available fragments.

        related = self.fragment.get_relations(sequence)

        if related:
            limit = len(related) - 1

            if direction < 0:
                if i is None:
                    i = limit
                elif i > 0:
                    i -= 1
                else:
                    i = None

            elif direction > 0:
                if i is None:
                    i = 0
                elif i < limit:
                    i += 1
                else:
                    i = None

        # Show similarity to the selected fragment.

        if i is not None:
            self.show_similarity(related[i])

        # Update the position in the sequence.

        if direction < 0:
            self.left_rotation = i
        else:
            self.right_rotation = i

        return self.show_fragment(self.get_rotation_fragment())

    def stop(self):

        "Stop and select any step fragment as the current fragment."

        if self.have_step():
            self.select_fragment(self.get_step_fragment())
        elif self.have_rotation():
            self.select_fragment(self.get_rotation_fragment())

        self.show_viewed_fragment()
    
    def playFile(self, fragment, visited, sock):
        if visited:
            playfile = audiopath + "ExcerptBrunaSoplo.wav"
            sound = AudioSegment.from_file(playfile, format="wav")
            play(sound)   
            self.show_fragment(fragment)


        split = fragment.split(":")
        filename = split[0]
        duration = split[1].split("-")

        start = float(duration[0]) 
        end = float(duration[1])

        playfile = audiopath + filename + ".wav"
        sound = AudioSegment.from_file(playfile, format="wav")

        #Times 1000 to go from seconds to milliseconds
        splice = sound[start*1000:end*1000]
        play(splice)

        #Empty the socket so we do not compare data we got before playback of audiofile and data recieved after
        empty_socket(sock)       


class Fragment:

    "A fragment abstraction employing a directory."

    def __init__(self, identifier, datadir):
        self.identifier = identifier
        self.datadir = datadir

        # Initialise the fragment identifier from a file if appropriate.

        if self.identifier is None:
            self.identifier = self.get_data("fragment")

    # Fragment directory contents.

    def get_data(self, datatype):

        "Return the textual content for the fragment of the given 'datatype'."

        textfile = join(self.datadir, datatype)
        return readfile(textfile)

    def get_relations(self, kind):

        "Return a collection of relations of the given 'kind'."

        return Related(join(self.datadir, kind)) 

class Related:

    "Collections of related fragments."

    def __init__(self, datadir):
        self.datadir = datadir
        self.length = isdir(self.datadir) and len(listdir(self.datadir)) or 0

    def __getitem__(self, n):

        "Return an object to access the related fragment in position 'n'."

        if n >= len(self):
            raise IndexError(n)

        return Fragment(None, join(self.datadir, str(n)))

    def __len__(self):

        "Return the number of related fragments of this collection's kind."

        return self.length

    def __nonzero__(self):
        return len(self) and True or False

# Interface classes.

class Prompter:

    "A class responsible for prompting and obtaining input."

    def __init__(self, out):

        "Initialise the prompter with the given 'out' stream."

        self.out = out

    # Input methods.

    def get_input(self, prompt):

        "Prompt and return input."

        print(prompt, end="", file=self.out)
        s = input()
        print(file=self.out)
        return s

# Interface functions.

def backtrack(explorer, prompter):

    "Remove recent history from the 'explorer'."

    out = prompter.out
    show_visited(explorer, prompter)

    while True:
        i = prompter.get_input("position> ")
        if not i:
            break

        try:
            i = int(i)
            identifier = explorer.visited[i]
            del explorer.visited[i:]
            explorer.select_fragment(identifier)
        except (IndexError, ValueError):
            print("Bad position.", file=out)

        if explorer.fragment:
            break

    explorer.show_fragment()

def jump(explorer, prompter):

    "Obtain a fragment identifier for the 'explorer'."

    while True:
        identifier = prompter.get_input("fragment> ")

        if identifier:
            explorer.select_fragment(identifier)
        else:
            explorer.select_random_fragment()

        if explorer.fragment:
            break

    fragmentidentifier = explorer.show_fragment()
    return fragmentidentifier

def show_visited(explorer, prompter):

    "Show visited fragments in the 'explorer'."

    out = prompter.out

    for i, identifier in enumerate(explorer.visited):
        print("%s) %s" % (i, identifier), file=out)

    print(file=out)

#Remove data from the socketbuffer
def empty_socket(sock):
    input = [sock]
    while 1:
        inputready, o, e = select.select(input,[],[], 0.0)
        if len(inputready)==0: break
        for s in inputready: s.recv(1)

def description():
    print("\n(1)First turn on \"Acceleration\" and \"Rotation\" in the SensorUDP app and \"SEND DATA\" to the IP and Port shown above. The computer and the mobile phone has to be connected to the same WiFi")
    print("If you do not have the \"SensorUDP\" app, download it from \"Play Store\"\n")
    print("(2)Then select a fragment to start or press Enter/Return for a random fragment.", file=out)
    print("\n(3)To quit, press \"CONTROL + C\"\n")


# Main program.
if __name__ == "__main__":
    print(__doc__)
    
    # Obtain the output directory.

    if len(sys.argv) < 2:
        print("Need the output directory to explore.", file=sys.stderr)
        sys.exit(1)

    datadir = join(sys.argv[1], "data")

    if not isdir(datadir):
        print("Need the output directory containing a subdirectory called data.", file=sys.stderr)
        sys.exit(1)

    metrics = False
    if len(sys.argv) == 3 and sys.argv[2] == "showMetrics":
        print("Metrics is turned on")
        metrics = True

    # Initialise the explorer.

    out = sys.stdout
    explorer = Explorer(datadir, out)
    prompter = Prompter(out)

    # Choose a fragment to begin with.
    explorer.show_fragments()

    # Set up UDP
    sock = mlE.socketUDP()
            
    dataStream = mlE.FeatureBox()
    
    # pData is previous data initialized.
    # Used to determine if new data is different to previous data
    pData = ''

    #Describing how to interact
    description()
    fragment, visited = jump(explorer, prompter)

    # Play the first file
    explorer.playFile(fragment, visited, sock)

    
    # Begin loop
    while True:
        data = sock.recv(1024) # buffer size is 1024 bytes
        
        # Check to see if collected data is different to previous data
        # And will restart loop to collect new data without
        # executing the rest of the loop
        if data == pData:
            continue
        # If the new data is novel continue with operations
        pData = data
        
        dataStream.update(data)
        if metrics:
            dataStream.plot()
        
        # If a step has been detected run an audiofile
        if (dataStream.detectStep()):
            print("step")
            fragment, visited = explorer.forward()
            if visited:
                fragment = explorer.select_random_fragment()
            explorer.playFile(fragment, visited, sock)

        # This program use rotation in X, Y and Z direction. 
        # This means for detecting rotation the orientation of the
        # phone does not matter. However, the phone needs to be pointing
        # the right way up for right rotation of user to be recorded as right
        # rotation for the phone. 
        
        #Check the sum of the stack of gyro values is above or belove a certain threshold.
        if(dataStream.detectRotLeft()):
            print("rotation left")  
            fragment, visited = explorer.rotate(-1) 
            if visited:
                fragment = explorer.select_random_fragment() 
            explorer.playFile(fragment, visited, sock)
        elif(dataStream.detectRotRight()):
            print("rotation right")
            fragment, visited = explorer.rotate(1)
            if visited:
                fragment = explorer.select_random_fragment()
            explorer.playFile(fragment, visited, sock)
