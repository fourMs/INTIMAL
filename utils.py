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

# Comparison functions.

def cmp_value_lengths(a, b):

    """
    Compare the (key, value) tuples 'a' and 'b' according to the length of
    their values.
    """

    return cmp(len(a[1]), len(b[1]))

def cmp_value_lengths_and_keys(a, b):

    """
    Compare the (key, value) tuples 'a' and 'b' according to the length of
    their values and their keys.
    """

    akey = len(a[1]), a[0]
    bkey = len(b[1]), b[0]
    return cmp(akey, bkey)

def cmp_values(a, b):

    "Compare the (key, value) tuples 'a' and 'b' according to their values."

    return cmp(a[1], b[1])

# Collection functions.

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
