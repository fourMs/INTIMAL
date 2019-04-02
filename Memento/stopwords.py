#!/usr/bin/env python
# -*- coding: utf-8

"""
Stop word filtering.

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

Part-of-speech tags originate from spaCy and include...

ADJ - adjective
ADV - adverb
NOUN - common noun
PNOUN - proper noun
VERB - verb
"""

from objects import Term

class POSFilter:

    "A way of filtering stop-words from text."

    def __init__(self, tags=None):

        "Initialise the filter with 'tags' of words to preserve."

        if tags is None:
            self.tags = ("NOUN", "PROPN", "ADJ")
        else:
            self.tags = tags

    def filter_words(self, words):

        "Filter 'words' according to part-of-speech roles."

        l = []

        for word in words:
            if not isinstance(word, Term) or word.tag in self.tags:
                l.append(word)

        return l

# vim: tabstop=4 expandtab shiftwidth=4
