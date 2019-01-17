#!/usr/bin/env python
# -*- coding: utf-8

"""
Stop word filtering.
"""

from objects import Term

def filter_terms_by_pos(terms):

    "Filter 'terms' according to part-of-speech roles."

    l = []

    for term in terms:
        if not isinstance(term, Term) or term.tag in ("NOUN", "PROPN", "ADJ", "VERB"):
            l.append(term)

    return l

# vim: tabstop=4 expandtab shiftwidth=4
