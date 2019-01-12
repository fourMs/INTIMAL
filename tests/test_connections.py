#!/usr/bin/env python
# -*- coding: utf-8

"""
Test the connection abstraction.
"""

from test_support import set_verbose, show
from objects import Connection, Fragment
import sys

# Test data.

f1 = Fragment("A1", 10, 20, "Parent", "Category")
f2 = Fragment("A2", 50, 60, "Parent", "Category")

c1 = Connection([], [f1, f2])

# Test cases.

def test_relations():
    show("%r.relations()" % c1, c1.relations(), [(f1, [f2]), (f2, [f1])])

def main():
    test_relations()

if __name__ == "__main__":
    set_verbose()
    main()

# vim: tabstop=4 expandtab shiftwidth=4
