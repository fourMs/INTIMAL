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
        word = unicode(term)

        # Add title-cased words, incorporating any filler words.

        if word.istitle():

            # Sometimes articles appear at the start of sentences. Sometimes
            # they are part of entities.

            if word.lower() in filler_words:
                filler.append(term)

            # Other words cause any filler words to be incorporated.

            else:
                if filler:
                    entity += filler
                    filler = []
                entity.append(term)

        # Queue up filler words only with confirmed entities.

        elif entity and word in filler_words:
            filler.append(term)

        # Handle other words.

        else:
            # Produce any held entity.

            if entity:
                emit_entity(l, entity)
                entity = []

            # Produce any trailing filler words.

            if filler:
                l += filler
                filler = []

            l.append(term)

    if entity:
        emit_entity(l, entity)

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
                emit_entity(l, entity)
            entity = [term]

        elif word in units:
            entity.append(term)
            emit_entity(l, entity)
            entity = []

        else:
            if entity:
                emit_entity(l, entity)
                entity = []

            l.append(term)

    if entity:
        emit_entity(l, entity)

    return l

def emit_entity(l, entity):

    "Add to 'l' the given 'entity'."

    if len(entity) > 1:
        l.append(" ".join(map(unicode, entity)))
    else:
        l.append(entity[0])

# vim: tabstop=4 expandtab shiftwidth=4
