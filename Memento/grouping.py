#!/usr/bin/env python3
# -*- coding: utf-8

"""
Simple grouping of words into terms.

Copyright (C) 2018, 2019 University of Oslo

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.

----

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
        word = str(term)

        # Add title-cased words, incorporating any filler words.

        if word.istitle():

            # Sometimes articles appear at the start of sentences. Sometimes
            # they are part of entities.

            if word.lower() in filler_words:
                if not entity:
                    l.append(term)
                else:
                    filler.append(term)

            # Reject various word roles in compound terms.

            elif tag in ("ADP", "DET"):
                end_entity(l, entity, filler)
                l.append(term)

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

            end_entity(l, entity, filler)
            l.append(term)

    # Produce any held entity.

    end_entity(l, entity, filler)
    return l

def group_quantities(terms):

    "Group 'terms' into entities for quantities."

    units = ["años", "días"]
    l = []
    entity = []

    for term in terms:
        word = str(term)

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
        l.append(" ".join(map(str, entity)))
    else:
        l.append(entity[0])

def end_entity(l, entity, filler):

    "Add to 'l' any given 'entity' plus 'filler' words."

    if entity:
        emit_entity(l, entity)
        del entity[:]

    # Produce any trailing filler words.

    if filler:
        l += filler
        del filler[:]

# vim: tabstop=4 expandtab shiftwidth=4
