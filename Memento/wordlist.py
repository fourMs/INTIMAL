#!/usr/bin/env python
# -*- coding: utf-8

"""
Word list functionality.

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

from inputs import get_list_from_file
import codecs

class Wordlist:

    "A word list used for filtering terms."

    def __init__(self, words):
        self.words = set(words)

    def __repr__(self):
        return "Wordlist(%r)" % list(self.words)

    def filter_words(self, words):

        "Return a copy of 'words' with those not in this word list omitted."

        l = []

        for word in words:

            # Convert terms/words to a specific string form.

            if unicode(word) in self.words:
                l.append(word)

        return l

def get_wordlist_from_file(filename):

    "Return a word list abstraction for the words defined in 'filename'."

    if not filename:
        return None

    return Wordlist(get_list_from_file(filename))

# vim: tabstop=4 expandtab shiftwidth=4
