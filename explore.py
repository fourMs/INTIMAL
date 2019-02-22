#!/usr/bin/env python
# -*- coding: utf-8

"""
Explore the generated data.
"""

from os import listdir
from os.path import join
import codecs
import sys

def readfile(filename):

    "Return the text in 'filename'."

    f = codecs.open(filename, encoding="utf-8")
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

    def get_fragments(self):

        "Return all the fragment identifiers."

        return listdir(self.datadir)

    def select_fragment(self, fragment):

        "Select the given 'fragment'."

        if fragment not in self.get_fragments():
            return

        # Reset stepping and rotation.

        self.fragment = fragment
        self.step = None
        self.rotation = None

    # Fragment directory contents.

    def get_fragment_dir(self, fragment):

        "Return the directory for 'fragment'."

        return join(self.datadir, fragment)

    def get_fragment_text(self, fragment):

        "Return the textual content of 'fragment'."

        dirname = self.get_fragment_dir(fragment)
        textfile = join(dirname, "text")
        return readfile(textfile)

    def get_related_fragment_dir(self, fragment, kind):

        """
        Return the directory for 'fragment' containing related fragment details
        of the given 'kind'.
        """

        dirname = self.get_fragment_dir(fragment)
        return join(dirname, kind)

    def get_limit_related_fragments(self, fragment, kind):

        """
        For 'fragment', return the position limit of the related fragments of
        the given 'kind'.
        """

        dirname = self.get_related_fragment_dir(fragment, kind)
        positions = map(int, listdir(dirname))
        if positions:
            return max(positions)
        else:
            return None

    def get_num_related_fragments(self, fragment, kind):

        """
        For 'fragment', return the number of related fragments of the given
        'kind'.
        """

        dirname = self.get_related_fragment_dir(fragment, kind)
        return len(listdir(dirname))

    def get_related_fragment(self, fragment, kind, n):

        """
        For 'fragment', return the fragment identifier of the related fragment
        of the given 'kind' in position 'n'.
        """

        dirname = self.get_related_fragment_dir(fragment, kind)
        filename = join(dirname, str(n))
        return readfile(filename)

    # Convenience methods.

    def get_rotation_fragment(self):

        "Return the identifier of the current rotation fragment."

        if self.rotation is not None:
            return self.get_related_fragment(self.fragment, "rotation", self.rotation)
        else:
            return self.fragment

    def get_step_fragment(self):

        "Return the identifier of the current step fragment."

        if self.step is not None:
            return self.get_related_fragment(self.fragment, "translation", self.step)
        else:
            return self.fragment

    # Input methods.

    def get_input(self):

        "Prompt and return input."

        print >>self.out, "> ",
        s = raw_input()
        print >>self.out
        return s

    # Output methods.

    def show_fragments(self):

        "Show all the fragment identifiers."

        fragments = self.get_fragments()
        fragments.sort()
        for fragment in fragments:
            print >>self.out, fragment

    def show_fragment(self, fragment=None):

        "Show the given 'fragment' details or those of the current fragment."

        fragment = fragment or self.fragment

        print >>self.out, fragment
        print >>self.out, self.get_fragment_text(fragment)
        print >>self.out

        if self.step is None:
            print >>self.out, "%d fragments ahead." % self.get_num_related_fragments(fragment, "translation")
            print >>self.out

    # Navigation methods.

    def move_forward(self):

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

        limit = self.get_limit_related_fragments(self.fragment, "translation")

        if limit is not None:
            if self.step is None:
                self.step = 0
            elif self.step < limit:
                self.step += 1
            
            print >>self.out, "Step #%d." % self.step
            print >>self.out

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

        limit = self.get_limit_related_fragments(self.fragment, "rotation")

        if limit is not None:
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

        self.show_fragment(self.get_rotation_fragment())

    def stop(self):

        "Stop and select any rotation or step fragment as the current fragment."

        if self.rotation is not None:
            self.select_fragment(self.get_rotation_fragment())
        elif self.step is not None:
            self.select_fragment(self.get_step_fragment())

        self.show_fragment()

def jump(explorer):

    "Obtain a fragment identifier for the 'explorer'."

    while True:
        fragment = explorer.get_input()
        explorer.select_fragment(fragment)
        if explorer.fragment:
            break

    explorer.show_fragment()

# Main program.

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print >>sys.stderr, "Need the data directory to explore."
        sys.exit(1)

    # Initialise the explorer.

    out = codecs.getwriter("utf-8")(sys.stdout)
    explorer = Explorer(sys.argv[1], out)

    # Choose a fragment to begin with.

    print >>out, "Select a fragment to start."
    explorer.show_fragments()
    jump(explorer)

    # Loop, accepting commands, and performing movements.

    while True:
        command = explorer.get_input()

        if command in ("q", "quit"):
            break
        elif command in ("f", "forward"):
            explorer.move_forward()
        elif command in ("s", "stop"):
            explorer.stop()
        elif command in ("l", "left"):
            explorer.rotate(-1)
        elif command in ("r", "right"):
            explorer.rotate(1)
        elif command in ("j", "jump"):
            jump(explorer)
        else:
            print >>out, "Bad command."

# vim: tabstop=4 expandtab shiftwidth=4
