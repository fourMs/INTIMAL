#!/usr/bin/env python
# -*- coding: utf-8

"""
Simple grouping of words into terms.
"""

def group_words(words):

    "Group 'words' into terms."

    words = group_names(words)
    words = group_quantities(words)
    return words

def group_names(words):

    "Group 'words' into terms for names."

    # NOTE: Use word features to support this correctly.
    filler_words = ["de", "la", "las", "lo", "los"]

    l = []
    term = []
    filler = []

    for word in words:

        # Add upper-cased words, incorporating any filler words.

        if word.isupper() or word.istitle():
            if filler:
                term += filler
                filler = []
            term.append(word)

        # Queue up filler words.

        elif term and word in filler_words:
            filler.append(word)

        # Handle other words.

        else:
            if term:
                l.append(" ".join(term))
                term = []
            if filler:
                l += filler
                filler = []
            l.append(word)

    if term:
        l.append(" ".join(term))
    if filler:
        l += filler
    return l

def group_quantities(words):

    "Group 'words' into terms for quantities."

    units = [u"años", u"días"]
    l = []
    term = []

    for word in words:
        if word.isdigit():
            if term:
                l.append(" ".join(term))
            term = [word]
        elif word in units:
            term.append(word)
            l.append(" ".join(term))
            term = []
        else:
            if term:
                l.append(" ".join(term))
                term = []
            l.append(word)

    if term:
        l.append(" ".join(term))
    return l

# vim: tabstop=4 expandtab shiftwidth=4
