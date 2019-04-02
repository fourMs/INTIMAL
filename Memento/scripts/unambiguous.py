#!/usr/bin/env python
# -*- coding: utf-8

"""
Process term lists and attempt to produce synonyms.
"""

from collections import defaultdict
from nltk.corpus import wordnet as wn
import codecs
import sys

f = codecs.open(sys.argv[1], encoding="utf-8")
senses = codecs.open(sys.argv[2], "w", encoding="utf-8")

d = defaultdict(list)

try:
    for line in f.readlines():
        word = line.strip().rsplit(None, 1)[0]

        synsets = wn.synsets("_".join(word.split()), "n", lang="spa")
        if len(synsets) == 1:
            d[synsets[0].name()].append(word)

    l = d.items()
    l.sort()

    for name, words in l:
        print >>senses, name, "/".join(words)

finally:
    f.close()
    senses.close()

# vim: tabstop=4 expandtab shiftwidth=4
