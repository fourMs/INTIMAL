#!/usr/bin/env python
# -*- coding: utf-8

"""
Stemming using NLTK.
"""

from nltk.stem.snowball import SnowballStemmer

def stem_words(words):
    stemmer = SnowballStemmer("spanish")
    l = []
    for word in words:
        l.append(stemmer.stem(word))
    return l

# vim: tabstop=4 expandtab shiftwidth=4
