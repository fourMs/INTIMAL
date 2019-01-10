#!/usr/bin/env python
# -*- coding: utf-8

"""
Stop word filtering.
"""

from nltk.corpus import stopwords

# Provisional stop words.
# NOTE: Should be in a file, but really should be provided by NLTK or similar.
# NOTE: Moreover, these stop words would be better filtered out using
# NOTE: part-of-speech tagging.

stop_words = [u"ahí", u"da", u"entonces", u"si", u"u"]

def no_stop_words(words):
    l = []

    # NLTK stop words. These may not be entirely appropriate or sufficient for
    # this application.

    stop = stop_words + stopwords.words("spanish")

    for word in words:
        if not word.lower() in stop:
            l.append(word)

    return l

# vim: tabstop=4 expandtab shiftwidth=4
