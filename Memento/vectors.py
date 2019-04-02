#!/usr/bin/env python
# -*- coding: utf-8

"""
Term vector computation.

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

def combine_term_vectors(vectors):

    "Return the result of combining the given term 'vectors'."

    if not vectors:
        return {}

    d = {}

    for term, value in vectors[0].items():
        d[term] = value

    # Take each vector in turn, trying to find terms in the other vectors.

    for vector in vectors[1:]:
        for term in d.keys():

            # Remove absent terms from the result.

            if not vector.has_key(term):
                del d[term]

            # Combine term values with the result.

            else:
                d[term] *= vector[term]

    return d

def get_term_vector_similarity(vectors, similarity=None):

    "Return the cosine measure computed from the term vectors."

    d = similarity or combine_term_vectors(vectors)
    dp = sum(d.values())
    mp = product(map(magnitude, vectors))
    return dp / mp

# Utility functions.

def magnitude(vector):

    "Return the magnitude of 'vector'."

    result = 0

    for term, value in vector.items():
        result += value ** 2

    return float(result) ** 0.5

def product(values):

    "Return the product of 'values'."

    return reduce(lambda a, b: a * b, values)

# vim: tabstop=4 expandtab shiftwidth=4
