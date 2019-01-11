#!/usr/bin/env python
# -*- coding: utf-8

"""
Elementary text handling.
"""

import unicodedata

# Word processing functions.

def lower(words):

    "Convert 'words' to lower case unless a multi-word term."

    # NOTE: Could usefully employ part-of-speech tags to avoid lower-casing
    # NOTE: proper nouns.

    l = []
    for word in words:
        if not " " in word:
            l.append(word.lower())
        else:
            l.append(word)
    return l

def _normalise_accents(s):

    "Convert in 's' all grave accents to acute accents."

    return unicodedata.normalize("NFC",
        unicodedata.normalize("NFD", s).replace(u"\u0300", u"\u0301"))

normalise_accents = lambda l: map(_normalise_accents, map(unicode, l))

punctuation = ",;.:?!"

def is_punctuation(s):
    for c in s:
        if c not in punctuation:
            return False
    return True

def remove_punctuation(s):
    for c in punctuation:
        s = s.replace(c, "")
    return s

def only_words(words):

    "Filter out non-words, principally anything that is punctuation."

    l = []
    for word in words:
        word = remove_punctuation(word).strip()
        if word:
            l.append(word)
    return l

# General text operations.

def to_text(i):

    "Return instance 'i' in textual form."

    if isinstance(i, (list, tuple)):
        return " ".join(map(to_text, i))
    else:
        return unicode(i).encode("utf-8")

# vim: tabstop=4 expandtab shiftwidth=4
