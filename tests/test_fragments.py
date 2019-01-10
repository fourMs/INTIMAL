#!/usr/bin/env python
# -*- coding: utf-8

"""
Test the fragment abstraction.
"""

from objects import Fragment, Term
import sys

# Test output.

verbose = False

def set_verbose():
    global verbose
    args = sys.argv[1:]
    if "-v" in args or "--verbose" in args:
        verbose = True

def show(text, result, expected):
    print result == expected,
    if verbose:
        print text,
    print result, expected

# Test data.

t1 = Term("man", ["bloke", "dude", "guy", "lad", "male", "man"])
t2 = Term("boy", ["boy", "kid", "lad", "male"])
t3 = Term("woman", ["lady", "woman"])
t4 = Term("man", ["adult_male", "gentleman's_gentleman", "man", "valet"])

f1 = Fragment("A1", 10, 20, "Parent", "Category", ["just", "another", "guy"])
f2 = Fragment("A1", 40, 50, "Parent", "Category", ["yet", "another", t2])
f3 = Fragment("A2", 10, 20, "Parent", "Category")
f4 = Fragment("A2", 10, 20, "Parent", "Different category")
f5 = Fragment("A1", 40, 50, "Parent", "Category", ["just", "another", t1])
f6 = Fragment("A3", 100, 200, "P", "C", ["discretion", "of", "the", "gentleman's", "gentleman"])

# Test cases.

def test_comparison():
    show("%r == %r" % (f1, f1), f1 == f1, True)
    show("%r == %r" % (f1, f2), f1 == f2, False)

    show("%r != %r" % (f1, f1), f1 != f1, False)
    show("%r != %r" % (f1, f2), f1 != f2, True)

    show("%r < %r" % (f1, f2), f1 < f2, True)
    show("%r == %r" % (f1, f2), f1 == f2, False)
    show("%r > %r" % (f1, f2), f1 > f2, False)

    show("%r == %r" % (f1, f3), f1 == f3, False)

def test_contains():
    show("%r in %r" % (t1, f1), t1 in f1, True)
    show("%r in %r" % (t2, f1), t2 in f1, False)
    show("%r in %r" % (t3, f1), t3 in f1, False)

    show("%r in %r" % (t1, f2), t1 in f2, True)
    show("%r in %r" % (t2, f2), t2 in f2, True)
    show("%r in %r" % (t3, f2), t3 in f2, False)

    show("%r in %r" % (t4, f6), t4 in f6, True)

def test_mapping():
    d = {}
    d[f1] = "f1"
    d[f2] = "f2"
    d[f3] = "f3"

    show("d.get(%r)" % f1, d.get(f1), "f1")
    show("d.get(%r)" % f2, d.get(f2), "f2")
    show("d.get(%r)" % f3, d.get(f3), "f3")
    show("d.get(%r)" % f4, d.get(f4), None)

def test_truth():
    show("bool(%r)" % f1, bool(f1), True)
    show("bool(%r)" % f2, bool(f2), True)
    show("bool(%r)" % f3, bool(f3), False)
    show("bool(%r)" % f4, bool(f4), False)

def test_intersection():
    show("%r.intersection(%r)" % (f1, f2), f1.intersection(f2), ["another"])
    show("%r.intersection(%r)" % (f1, f3), f1.intersection(f3), [])
    show("%r.intersection(%r)" % (f5, f2), f5.intersection(f2), ["another", t1])

def main():
    test_comparison()
    test_contains()
    test_mapping()
    test_truth()
    test_intersection()

if __name__ == "__main__":
    set_verbose()
    main()

# vim: tabstop=4 expandtab shiftwidth=4
