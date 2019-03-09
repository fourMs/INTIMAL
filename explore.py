#!/usr/bin/env python2.7
# -*- coding: utf-8

"""
Explore the generated data.
"""

from os import listdir
from os.path import isdir, join
from locale import getlocale, setlocale, LC_CTYPE
import codecs
import random
import sys

encoding = "utf-8"

def readfile(filename):

    "Return the text in 'filename'."

    f = codecs.open(filename, encoding=encoding)
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
        self.rotation = None

        # Remember visited fragments.

        self.visited = []

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
        self.rotation = None

    def select_random_fragment(self):

        "Select a random fragment."

        l = random.sample(self.get_fragments(), 1)
        if l:
            self.select_fragment(l[0])

    # Fragment directory contents.

    def open_fragment(self, identifier):

        "Return a fragment object for the 'identifier'."

        return Fragment(identifier, join(self.datadir, identifier))

    # Convenience methods.

    def get_rotation_fragment(self):

        "Return the identifier of the current rotation fragment."

        if self.rotation is not None:
            related = self.fragment.get_relations("rotation")
            fragment = related[self.rotation]
            return fragment.get_data("fragment")
        else:
            return self.fragment.identifier

    def get_step_fragment(self):

        "Return the identifier of the current step fragment."

        if self.have_step():
            related = self.fragment.get_relations("translation")
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
            print >>self.out, identifier

    def show_fragment(self, identifier=None):

        """
        Show the given fragment details for the given 'identifier' or those of
        the current fragment.
        """

        fragment = identifier and self.open_fragment(identifier) or self.fragment

        if fragment.identifier in self.visited:
            print >>self.out, "VISITED!"
            print >>self.out
        else:
            print >>self.out, fragment.identifier
            print >>self.out, fragment.get_data("category")
            print >>self.out
            print >>self.out, fragment.get_data("text")
            print >>self.out

        if self.step is None:
            related = fragment.get_relations("translation")
            print >>self.out, "%d fragments ahead." % len(related)
            print >>self.out

        # Remember this fragment as having been visited.

        self.visited.append(fragment.identifier)

    def show_similarity(self, fragment):

        "Show similarity to the given related 'fragment'."

        print >>self.out, "Measure:", fragment.get_data("measure")
        print >>self.out, "Similarity:", fragment.get_data("similarity")
        print >>self.out

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

        if self.rotation is not None:
            self.select_fragment(self.get_rotation_fragment())

        # Step forward to the first or subsequent fragments. If reaching the
        # limit, select the final fragment in the sequence and step forward from
        # it.

        related = self.fragment.get_relations("translation")

        if related:
            limit = len(related) - 1

            if self.step is None:
                self.step = 0
            elif self.step < limit:
                self.step += 1
            
            print >>self.out, "Step #%d..." % self.step
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

        # Cycle through the available fragments.

        related = self.fragment.get_relations("rotation")

        if related:
            limit = len(related) - 1

            if direction < 0:
                if self.rotation is None:
                    self.rotation = limit
                elif self.rotation > 0:
                    self.rotation -= 1
                else:
                    self.rotation = None

            elif direction > 0:
                if self.rotation is None:
                    self.rotation = 0
                elif self.rotation < limit:
                    self.rotation += 1
                else:
                    self.rotation = None

        if self.rotation is not None:
            self.show_similarity(related[self.rotation])

        self.show_fragment(self.get_rotation_fragment())

    def stop(self):

        "Stop and select any step fragment as the current fragment."

        if self.have_step():
            self.select_fragment(self.get_step_fragment())

        self.show_fragment()

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

    def __getitem__(self, n):

        "Return an object to access the related fragment in position 'n'."

        return Fragment(None, join(self.datadir, str(n)))

    def __len__(self):

        "Return the number of related fragments of this collection's kind."

        return isdir(self.datadir) and len(listdir(self.datadir)) or 0

    def __nonzero__(self):
        return len(self) and True or False

# Interface classes.

class Prompter:

    "A class responsible for prompting and obtaining input."

    def __init__(self, out, encoding):

        """
        Initialise the prompter with the given 'out' stream and input
        'encoding'.
        """

        self.out = out
        self.encoding = encoding

    # Input methods.

    def get_input(self, prompt):

        "Prompt and return input."

        print >>self.out, prompt,
        s = raw_input()
        print >>self.out
        return unicode(s, self.encoding)

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
            print >>out, "Bad position."

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
        print >>out, "%s) %s" % (i, identifier)

    print >>out

# Main program.

if __name__ == "__main__":

    # Obtain locale details.

    setlocale(LC_CTYPE, "")
    lang, console_encoding = getlocale(LC_CTYPE)

    # Obtain the output directory.

    if len(sys.argv) < 2:
        print >>sys.stderr, "Need the output directory to explore."
        sys.exit(1)

    datadir = join(sys.argv[1], "data")

    if not isdir(datadir):
        print >>sys.stderr, "Need the output directory containing a subdirectory called data."
        sys.exit(1)

    # Initialise the explorer.

    out = codecs.getwriter(console_encoding)(sys.stdout)
    explorer = Explorer(datadir, out)
    prompter = Prompter(out, console_encoding)

    # Choose a fragment to begin with.

    print >>out, "Select a fragment to start or press Enter/Return for a random fragment."
    explorer.show_fragments()
    jump(explorer, prompter)

    # Loop, accepting commands, and performing movements.

    while True:
        print >>out, "Which way? (%d fragments visited)" % \
                     len(explorer.visited)
        print >>out, "(b)acktrack, (f)orward, (l)eft, (r)ight, %s(j)ump, (v)isited, (q)uit" % \
                     (explorer.have_step() and "(s)top, " or "")

        command = prompter.get_input("> ")

        if command in ("q", "quit"):
            break
        elif command in ("f", "forward"):
            explorer.forward()
        elif command in ("s", "stop"):
            explorer.stop()
        elif command in ("l", "left"):
            explorer.rotate(-1)
        elif command in ("r", "right"):
            explorer.rotate(1)
        elif command in ("j", "jump"):
            print >>out, "Select a fragment or press Enter/Return for a random fragment."
            jump(explorer, prompter)
        elif command in ("v", "visited"):
            show_visited(explorer, prompter)
        elif command in ("b", "back", "backtrack"):
            backtrack(explorer, prompter)
        else:
            print >>out, "Bad command."

# vim: tabstop=4 expandtab shiftwidth=4
