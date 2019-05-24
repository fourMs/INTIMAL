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

encoding = "utf-8"

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

        self.show_fragment(self.get_step_fragment())

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

        self.show_fragment(self.get_rotation_fragment())

    def stop(self):

        "Stop and select any step fragment as the current fragment."

        if self.have_step():
            self.select_fragment(self.get_step_fragment())
        elif self.have_rotation():
            self.select_fragment(self.get_rotation_fragment())

        self.show_viewed_fragment()

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

    explorer.show_fragment()

def show_visited(explorer, prompter):

    "Show visited fragments in the 'explorer'."

    out = prompter.out

    for i, identifier in enumerate(explorer.visited):
        print("%s) %s" % (i, identifier), file=out)

    print(file=out)

# Main program.

if __name__ == "__main__":

    # Obtain the output directory.

    if len(sys.argv) < 2:
        print("Need the output directory to explore.", file=sys.stderr)
        sys.exit(1)

    datadir = join(sys.argv[1], "data")

    if not isdir(datadir):
        print("Need the output directory containing a subdirectory called data.", file=sys.stderr)
        sys.exit(1)

    # Initialise the explorer.

    out = sys.stdout
    explorer = Explorer(datadir, out)
    prompter = Prompter(out)

    # Choose a fragment to begin with.

    print("Select a fragment to start or press Enter/Return for a random fragment.", file=out)
    explorer.show_fragments()
    jump(explorer, prompter)

    # Loop, accepting commands, and performing movements.

    while True:
        print("Which way? (%d fragments visited, %d different)" % \
              (len(explorer.visited), len(set(explorer.visited))),
              file=out)
        print("(b)acktrack, (f)orward, (j)ump, (l)eft, (r)ight, (s)top, (t)ext, (v)isited, (q)uit",
              file=out)

        command = prompter.get_input("> ")

        # Movement commands.

        if command in ("f", "forward"):
            explorer.forward()
        elif command in ("s", "stop"):
            explorer.stop()
        elif command in ("l", "left"):
            explorer.rotate(-1)
        elif command in ("r", "right"):
            explorer.rotate(1)

        # Navigation commands.

        elif command in ("j", "jump"):
            print("Select a fragment or press Enter/Return for a random fragment.", file=out)
            jump(explorer, prompter)
        elif command in ("v", "visited"):
            show_visited(explorer, prompter)
        elif command in ("b", "back", "backtrack"):
            backtrack(explorer, prompter)

        # Informational commands.

        elif command in ("t", "text"):
            explorer.show_viewed_fragment()

        # Exit or unrecognised commands.

        elif command in ("q", "quit"):
            break
        else:
            print("Bad command.", file=out)
            print(file=out)

# vim: tabstop=4 expandtab shiftwidth=4
