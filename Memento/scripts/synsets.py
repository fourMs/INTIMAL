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
synonyms = codecs.open(sys.argv[2], "w", encoding="utf-8")
classes = codecs.open(sys.argv[3], "w", encoding="utf-8")
try:
    for line in f.readlines():
        word = line.strip()
        all_synonyms = set()
        all_pos = defaultdict(lambda: 0)

        # Obtain synonyms for the word.

        for synset in wn.synsets(word, lang="spa"):
            all_synonyms.update(synset.lemmas(lang="spa"))
            all_pos[synset.pos()] += 1

        # Output synonyms for the word.

        for synonym in all_synonyms:
            print >>synonyms, word, synonym

        # Find the dominant part of speech tag.

        if all_pos:
            pos_items = all_pos.items()
            pos_items.sort(key=lambda i: i[1])

            # Output the POS tag for the word.

            print >>classes, word, pos_items[-1][0]
finally:
    f.close()
    synonyms.close()
    classes.close()

# vim: tabstop=4 expandtab shiftwidth=4
