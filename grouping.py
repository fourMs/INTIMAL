#!/usr/bin/env python
# -*- coding: utf-8

"""
Simple grouping of words into terms.

An alternative approach to this may involve using named entity recognition in
toolkits such as spaCy.
"""

def group_words(terms):

    "Group 'terms' into entities."

    terms = group_names(terms)
    terms = group_quantities(terms)
    return terms

def group_names(terms):

    "Group 'terms' into entities for names."

    # NOTE: Use word features to support this correctly.
    filler_words = ["de", "la", "las", "lo", "los"]

    l = []
    entity = []
    filler = []

    for term in terms:
        word = unicode(term)

        # Add title-cased words, incorporating any filler words.

        if word.istitle():
            if filler:
                entity += filler
                filler = []
            entity.append(word)

        # Queue up filler words.

        elif entity and word in filler_words:
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
