#!/usr/bin/env python
# -*- coding: utf-8

"""
Word list functionality.
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
            if word in self.words:
                l.append(word)

        return l

def get_wordlist_from_file(filename):

    "Return a word list abstraction for the words defined in 'filename'."

    if not filename:
        return None

    return Wordlist(get_list_from_file(filename))

# vim: tabstop=4 expandtab shiftwidth=4
