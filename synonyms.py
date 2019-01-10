#!/usr/bin/env python
# -*- coding: utf-8

"""
Synonym mapping using WordNet.
"""

from objects import Term

from nltk.corpus import wordnet as wn

# Mapping via WordNet.

def map_to_synonyms(words):

    "Map 'words' to synonyms for normalisation."

    l = []
    for word in words:
        s = set()
        for synset in wn.synsets(word, lang="spa"):
            for synonym in synset.lemma_names(lang="spa"):
                s.add(synonym)
        l.append(Term(word, s))

    return l

# vim: tabstop=4 expandtab shiftwidth=4
