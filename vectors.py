#!/usr/bin/env python
# -*- coding: utf-8

"""
Term vector computation.

Term vectors are obtained from fragments and feature term frequencies. These
vectors are combined to produce similarity details for the contributing
fragments. The process of combination involves multiplying the frequencies
together and optionally applying a scaling factor (typically the inverse
document frequency of each term), producing a dot product of the vectors
involved.

An eventual similarity between fragments also involves the magnitude of the
term vectors. This, combined with the similarity details yields a measure that
may be interpreted as the cosine of an angle between the vectors, with a value
of 1 indicating an angle of 0 and thus complete similarity between vectors, and
with a value of 0 indicating a right angle and thus complete dissimilarity.

More details can be found here:

Vector space model: https://en.wikipedia.org/wiki/Vector_space_model

Related concepts are described here:

Bag of words model: https://en.wikipedia.org/wiki/Bag-of-words_model
Tf-idf: https://en.wikipedia.org/wiki/Tf%E2%80%93idf
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
