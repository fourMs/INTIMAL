#!/usr/bin/env python
# -*- coding: utf-8

"""
Common utilities.
"""

from collections import defaultdict

class CountingDict(defaultdict):

    """
    A simple counting dictionary with a plain dictionary string representation.
    """

    def __init__(self, start=0):
        defaultdict.__init__(self, lambda: start)

    def __repr__(self):
        l = []
        for key, value in self.items():
            l.append("%r: %r" % (key, value))
        return "{%s}" % ", ".join(l)

def get_relations(values):

    """
    Return the relations for each value in the given 'values' collection,
    providing entries of the form (value, other values).
    """

    l = []

    for i, value in enumerate(values):
        l.append((value, values[:i] + values[i+1:]))

    return l

def only_one(l):

    """
    Return the only element in 'l' if it only has one element. Otherwise, return
    None.
    """

    if len(l) == 1:

        # Handle sets as well as lists.

        for i in l:
            return i

    return None

# vim: tabstop=4 expandtab shiftwidth=4
