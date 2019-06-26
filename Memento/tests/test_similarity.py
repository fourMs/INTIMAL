#!/usr/bin/env python
# -*- coding: utf-8

"""
Test similarity computation.
"""

from test_support import set_verbose, show
from objects import Category, Fragment, Source, \
                    compare_fragments, get_fragment_similarity, \
                    inverse_document_frequencies, \
                    process_term_vectors, \
                    word_document_frequencies, word_frequencies
from text import only_words
import re

# Test data.

# http://www.gutenberg.org/files/22065/22065-h/22065-h.htm

source = "22065"

sentences = """\
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
    words = list(map(lambda s: s.lower(), words))
    fragments.append(Fragment(Source(source, i, i+1), category, words, sentence))

# Prepare connections for testing.

process_term_vectors(fragments)
connections = compare_fragments(fragments)



# Diagnostics.

def show_connections():
    for c in connections:
        print(c.measure(), c.similarity)
        for f in c.fragments:
            print(f.text)
        print()



# Test cases.

def test_similarity():
    show("get_fragment_similarity([%r, %r])" % (fragments[0], fragments[2]),
         get_fragment_similarity([fragments[0], fragments[2]]),
         {"pollo" : 1})

    show("get_fragment_similarity([%r, %r])" % (fragments[0], fragments[-2]),
         get_fragment_similarity([fragments[0], fragments[-2]]),
         {"pollo" : 1})

    show("get_fragment_similarity([%r, %r])" % (fragments[2], fragments[-2]),
         get_fragment_similarity([fragments[2], fragments[-2]]),
         {"el" : 10, "pobre" : 1, "pollo" : 1})

def test_frequencies():
    show("word_frequencies([%r, %r])" % (fragments[0], fragments[2]),
         word_frequencies([fragments[0], fragments[2]]),
         {"un" : 3, "día" : 1, "pollo" : 2, "entra" : 1, "en" : 1,
          "bosque" : 1, "el" : 2, "pobre" : 1, "cree" : 1, "que" : 1,
          "cielo" : 1, "ha" : 1, "caído" : 1, "sobre" : 1, "él" : 1})

    show("word_document_frequencies([%r, %r])" % (fragments[0], fragments[2]),
         word_document_frequencies([fragments[0], fragments[2]]),
         {"un" : 1, "día" : 1, "pollo" : 2, "entra" : 1, "en" : 1,
          "bosque" : 1, "el" : 1, "pobre" : 1, "cree" : 1, "que" : 1,
          "cielo" : 1, "ha" : 1, "caído" : 1, "sobre" : 1, "él" : 1})



def main():
    test_similarity()
    test_frequencies()

if __name__ == "__main__":
    set_verbose()
    main()

# vim: tabstop=4 expandtab shiftwidth=4
