#!/usr/bin/env python
# -*- coding: utf-8

"""
Term vector computation.
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
