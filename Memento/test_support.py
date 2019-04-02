#!/usr/bin/env python
# -*- coding: utf-8

"""
Test support.

Copyright (C) 2018, 2019 University of Oslo

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
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
