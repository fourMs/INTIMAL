#!/usr/bin/env python
# -*- coding: utf-8

"""
Synonym mapping using WordNet.
"""

from objects import Term

from nltk.corpus import wordnet as wn

# Mapping via WordNet.

def map_to_synonyms(words, lang="spa"):

    "Map 'words' to synonyms for normalisation."

    # NOTE: Could use part-of-speech information to filter synsets.

    l = []
    for word in words:
        senses = set()

        for synset in wn.synsets(word, lang=lang):
            senses.add(synset.name())

        # Create a term with the senses found for the word.

        l.append(Term(word, senses))

    return l

# vim: tabstop=4 expandtab shiftwidth=4
