#!/usr/bin/env python
# -*- coding: utf-8

"""
Process word lists.
"""

import codecs
import sys

f = codecs.open(sys.argv[1], encoding="utf-8")
f_out = codecs.getwriter("utf-8")(sys.stdout)
try:
    for line in f.readlines():
        line = line.strip()
        print >>f_out, line.lower()
finally:
    f.close()
    f_out.close()

# vim: tabstop=4 expandtab shiftwidth=4
