#!/usr/bin/env python
# -*- coding: utf-8

"""
Stop word filtering.
"""

from objects import Term

class POSFilter:

    "A way of filtering stop-words from text."

    def __init__(self, tags=None):

        "Initialise the filter with 'tags' of words to preserve."

        if tags is None:
            self.tags = ("NOUN", "PROPN", "ADJ", "VERB")
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
