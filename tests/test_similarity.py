#!/usr/bin/env python
# -*- coding: utf-8

"""
Test similarity computation.
"""

from test_support import set_verbose, show
from objects import Category, Fragment, \
                    compare_fragments, get_fragment_similarity, \
                    word_frequencies
from text import only_words
import re
import sys

# Test data.

# http://www.gutenberg.org/files/22065/22065-h/22065-h.htm

source = "22065"

sentences = u"""\
Un día un pollo entra en un bosque.
Una bellota cae en su cabeza.
El pobre pollo cree que el cielo ha caído sobre él.
Corre para informar al rey.
En el camino encuentran un pavo.
El pavo quiere ir con ellos a informar al rey que el cielo ha caído.
Ninguno de los pobres animales sabe el camino.
En este momento encuentran una zorra.
La zorra dice que quiere enseñarles el camino al palacio del rey.
Todos van con ella; pero ella los conduce a su cubil.
Aquí la zorra y sus cachorros se comen el pobre pollo y la gallina y el gallo y el pato y el ganso y el pavo.
Los pobres no van al palacio y no pueden informar al rey que el cielo ha caído sobre la cabeza del pobre pollo.\
""".split("\n")

category = Category("Spanish", "story")

# Simple word splitting.

pattern = re.compile(r"([ .,:;]+)")

def split_words(s):
    l = []
    for t in pattern.split(s):
        if t and t != " ":
            l.append(t)
    return l

# Prepare actual fragments for testing.

fragments = []

for i, sentence in enumerate(sentences):
    words = split_words(sentence)
    words = only_words(words)
    words = map(lambda s: s.lower(), words)
    fragments.append(Fragment(source, i, i+1, category, words, sentence))

# Prepare connections for testing.

connections = compare_fragments(fragments)



# Test cases.

def test_intersection():
    show("%r.intersection(%r)" % (fragments[0], fragments[2]),
         fragments[0].intersection(fragments[2]),
         [u"pollo"])
    show("%r.intersection(%r)" % (fragments[2], fragments[0]),
         fragments[2].intersection(fragments[0]),
         [u"pollo"])

    show("%r.intersection(%r)" % (fragments[0], fragments[-2]),
         fragments[0].intersection(fragments[-2]),
         [u"pollo"])
    show("%r.intersection(%r)" % (fragments[-2], fragments[0]),
         fragments[-2].intersection(fragments[0]),
         [u"pollo"])

    show("%r.intersection(%r)" % (fragments[2], fragments[-2]),
         fragments[2].intersection(fragments[-2]),
         [u"el", u"pobre", u"pollo", u"el"])
    show("%r.intersection(%r)" % (fragments[-2], fragments[2]),
         fragments[-2].intersection(fragments[2]),
         [u"el", u"pobre", u"pollo", u"el", u"el", u"el", u"el"])

def test_union():
    show("%r.union(%r)" % (fragments[0], fragments[2]),
         fragments[0].union(fragments[2]),
         [u"un", u"día", u"un", u"pollo", u"entra", u"en", u"un", u"bosque",
          u"el", u"pobre", u"pollo", u"cree", u"que", u"el", u"cielo", u"ha", u"caído", u"sobre", u"él"])

def test_similarity():
    show("get_fragment_similarity([%r, %r])" % (fragments[0], fragments[2]),
         get_fragment_similarity([fragments[0], fragments[2]]),
         {u"pollo" : 2})

    show("get_fragment_similarity([%r, %r])" % (fragments[0], fragments[-2]),
         get_fragment_similarity([fragments[0], fragments[-2]]),
         {u"pollo" : 2})

    show("get_fragment_similarity([%r, %r])" % (fragments[2], fragments[-2]),
         get_fragment_similarity([fragments[2], fragments[-2]]),
         {u"el" : 7, u"pobre" : 2, u"pollo" : 2})

def test_frequencies():
    show("word_frequencies([%r, %r])" % (fragments[0], fragments[2]),
         word_frequencies([fragments[0], fragments[2]]),
         {u"un" : 3, u"día" : 1, u"pollo" : 2, u"entra" : 1, u"en" : 1,
          u"bosque" : 1, u"el" : 2, u"pobre" : 1, u"cree" : 1, u"que" : 1,
          u"cielo" : 1, u"ha" : 1, u"caído" : 1, u"sobre" : 1, u"él" : 1})



def main():
    test_intersection()
    test_union()
    test_similarity()
    test_frequencies()

if __name__ == "__main__":
    set_verbose()
    main()

# vim: tabstop=4 expandtab shiftwidth=4
