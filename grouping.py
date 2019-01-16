#!/usr/bin/env python
# -*- coding: utf-8

"""
Simple grouping of words into terms.

An alternative approach to this may involve using named entity recognition in
toolkits such as spaCy.
"""

from objects import Term

def group_words(terms):

    "Group 'terms' into entities."

    terms = group_names(terms)
    terms = group_quantities(terms)
    return terms

def group_names(terms):

    "Group 'terms' into entities for names."

    # Word features might be used to support this correctly. However, merely
    # accumulating words of certain kinds can cause false positives.

    filler_words = ["de", "del", "la", "las", "lo", "los"]

    l = []
    entity = []
    filler = []

    for term in terms:
        tag = isinstance(term, Term) and term.tag or None
        word = unicode(term)

        # Add title-cased words, incorporating any filler words.

        if tag == "PROPN" or not tag and word.istitle():
            if filler:
                entity += filler
                filler = []
            entity.append(word)

        # Queue up filler words.

        elif entity and (tag in ("ADP", "DET") or not tag and word in filler_words):
            filler.append(word)

        # Handle other words.

        else:
            if entity:
                l.append(" ".join(entity))
                entity = []
            if filler:
                l += filler
                filler = []

            l.append(term)

    if entity:
        l.append(" ".join(entity))
    if filler:
        l += filler
    return l

def group_quantities(terms):

    "Group 'terms' into entities for quantities."

    units = [u"años", u"días"]
    l = []
    entity = []

    for term in terms:
        word = unicode(term)

        if word.isdigit():
            if entity:
                l.append(" ".join(entity))
            entity = [word]
        elif word in units:
            entity.append(word)
            l.append(" ".join(entity))
            entity = []
        else:
            if entity:
                l.append(" ".join(entity))
                entity = []
            l.append(term)

    if entity:
        l.append(" ".join(entity))
    return l

# vim: tabstop=4 expandtab shiftwidth=4
