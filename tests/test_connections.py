#!/usr/bin/env python
# -*- coding: utf-8

"""
Test the connection abstraction.
"""

from test_support import set_verbose, show
from objects import Category, Connection, Fragment, Source

# Test data.

cat1 = Category("Parent", "Category")

f1 = Fragment(Source("A1", 10, 20), cat1)
f2 = Fragment(Source("A2", 50, 60), cat1)

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
