#!/usr/bin/env python
# -*- coding: utf-8

"""
Word list functionality.
"""

import codecs

class Wordlist:

    "A word list used for filtering terms."

    def __init__(self, words):
        self.words = set(words)

    def filter_words(self, words):

        "Return 'words' with those not in this word list omitted."

        l = []

        for word in words:
            if word in self.words:
                l.append(word)

        return l

def get_wordlist_from_file(filename):

    "Return a word list abstraction for the words defined in 'filename'."

    l = []

    f = codecs.open(filename, encoding="utf-8")
    try:
        for line in f.xreadlines():
            line = line.strip()
            if line:
                l.append(line)
    finally:
        f.close()

    return Wordlist(l)

# vim: tabstop=4 expandtab shiftwidth=4
