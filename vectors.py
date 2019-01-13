#!/usr/bin/env python
# -*- coding: utf-8

"""
Term vector computation.
"""

from utils import CountingDict, get_relations

def combine_term_vectors(vectors, idf=None):

    "Return the result of combining the given term 'vectors'."

    d = CountingDict(1)

    # Take each vector in turn, trying to find terms in the other vectors.

    for vector, others in get_relations(vectors):
        for other in others:

            # Since terms may be considered equal generally but not for use as
            # dictionary keys, explicitly search for each term in each
            # collection.

            other_terms = other.keys()

            for term, value in vector.items():
                if term in other_terms:

                    # Scale the term weight if requested.

                    idf_term = idf and idf[term] or 1

                    # Employ the product when combining weights.

                    d[term] *= value * idf_term

    return d

def magnitude(vector):

    "Return the magnitude of 'vector'."

    result = 0

    for term, value in vector.items():
        result += value ** 2

    return float(result) ** 0.5

def product(values):

    "Return the product of 'values'."

    return reduce(lambda a, b: a * b, values)

def get_term_vector_similarity(vectors, similarity=None):

    "Return the cosine measure computed from the term vectors."

    d = similarity or combine_term_vectors(vectors)
    dp = sum(d.values())
    mp = product(map(magnitude, vectors))
    return dp / mp

# vim: tabstop=4 expandtab shiftwidth=4
