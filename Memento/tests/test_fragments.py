#!/usr/bin/env python
# -*- coding: utf-8

"""
Test the fragment abstraction.
"""

from test_support import set_verbose, show
from objects import Category, Fragment, Source

# Test data.

t1 = u"hombre"
t2 = u"niño"
t3 = u"mujer"
t4 = u"esposo"

cat1 = Category("Parent", "Category")
cat2 = Category("Parent", "Different category")
cat3 = Category("P", "C")

f1 = Fragment(Source("A1", 10, 20), cat1, [u"un", u"hombre"])
f2 = Fragment(Source("A1", 40, 50), cat1, [u"un", t2])
f3 = Fragment(Source("A2", 10, 20), cat1)
f4 = Fragment(Source("A2", 10, 20), cat2)
f5 = Fragment(Source("A1", 40, 50), cat1, [u"un", t1])
f6 = Fragment(Source("A3", 100, 200), cat3, [u"un", t4])

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

    show("%r in %r" % (t1, f2), t1 in f2, False)
    show("%r in %r" % (t2, f2), t2 in f2, True)
    show("%r in %r" % (t3, f2), t3 in f2, False)

    show("%r in %r" % (t4, f1), t4 in f1, False)
    show("%r in %r" % (t4, f2), t4 in f2, False)
    show("%r in %r" % (t4, f5), t4 in f5, False)
    show("%r in %r" % (t4, f6), t4 in f6, True)

def test_mapping():
    d = {}
    d[f1] = "f1"
    d[f2] = "f2"
    d[f3] = "f3"

    show("d.get(%r)" % f1, d.get(f1), "f1")
    show("d.get(%r)" % f2, d.get(f2), "f2")
    show("d.get(%r)" % f3, d.get(f3), "f3")
    show("d.get(%r)" % f4, d.get(f4), "f3")

def test_truth():
    show("bool(%r)" % f1, bool(f1), True)
    show("bool(%r)" % f2, bool(f2), True)
    show("bool(%r)" % f3, bool(f3), False)
    show("bool(%r)" % f4, bool(f4), False)

def test_vector():
    show("%r.get_term_vector()" % f1, f1.get_term_vector(), {u"un" : 1, u"hombre" : 1})
    show("%r.get_term_vector()" % f2, f2.get_term_vector(), {u"un" : 1, t2 : 1})
    show("%r.get_term_vector()" % f3, f3.get_term_vector(), {})

def main():
    test_comparison()
    test_contains()
    test_mapping()
    test_truth()
    test_vector()

if __name__ == "__main__":
    set_verbose()
    main()

# vim: tabstop=4 expandtab shiftwidth=4
