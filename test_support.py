#!/usr/bin/env python
# -*- coding: utf-8

"""
Test support.
"""

import sys

# Test output.

verbose = False

def set_verbose():
    global verbose
    args = sys.argv[1:]
    if "-v" in args or "--verbose" in args:
        verbose = True

def show(text, result, expected):
    print result == expected and "Success" or "Failure",
    if verbose:
        print text,
        print repr(result), repr(expected)
    else:
        print

# vim: tabstop=4 expandtab shiftwidth=4
