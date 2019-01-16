#!/usr/bin/env python
# -*- coding: utf-8

"""
Stop word filtering.

An alternative approach would involve part-of-speech tagging and the elimination
of words having particular roles.
"""

from nltk.corpus import stopwords
from objects import Term

# Provisional stop words.

stop_words = [u"ahí", u"da", u"entonces", u"si", u"u"]

def no_stop_words(terms):
    l = []

    # NLTK stop words. These may not be entirely appropriate or sufficient for
    # this application.

    stop = stop_words + stopwords.words("spanish")

    for term in terms:
        word = unicode(term)
        if not word.lower() in stop:
            l.append(term)

    return l

def filter_terms_by_pos(terms):

    "Filter 'terms' according to part-of-speech roles."

    l = []

    for term in terms:
        if not isinstance(term, Term) or term.tag in ("NOUN", "PROPN", "ADJ", "VERB"):
            l.append(term)

    return l

# vim: tabstop=4 expandtab shiftwidth=4
