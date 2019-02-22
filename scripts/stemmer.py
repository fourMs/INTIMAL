#!/usr/bin/env python
# -*- coding: utf-8

"""
Test PyStemmer and the Snowball stemming library.
"""

from Stemmer import Stemmer
import codecs
import sys

stemmer = Stemmer("spanish")

f = codecs.open(sys.argv[1], encoding="utf-8")
f_out = codecs.open(sys.argv[2], "w", encoding="utf-8")
try:
    for line in f.readlines():
        line = line.strip()
        words = line.split()
        stemmed = stemmer.stemWords(words)

        print >>f_out, " In:", line
        print >>f_out, "Out:", u" ".join(stemmed)
        print >>f_out
finally:
    f.close()
    f_out.close()

# vim: tabstop=4 expandtab shiftwidth=4
