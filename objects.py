#!/usr/bin/env python
# -*- coding: utf-8

"""
Textual abstractions.
"""

from text import text_from_words
from utils import CountingDict
from vectors import combine_term_vectors, get_term_vector_similarity

from collections import defaultdict
from itertools import combinations
from math import log
import re
import os.path

class Category:

    "A complete category description featuring a parent and child category."

    def __init__(self, parent, category):
        self.parent = parent
        self.category = category

    def __cmp__(self, other):
        return cmp(self.as_tuple(), other and other.as_tuple())

    def __hash__(self):
        return hash(self.as_tuple())

    def __repr__(self):
        return "Category(%r, %r)" % self.as_tuple()

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        return "%s-%s" % self.as_tuple()

    def as_tuple(self):
        return (self.parent, self.category)

    def complete(self):

        """
        Return whether the category is complete, having both parent and sub-
        category.
        """

        return self.parent and self.category

    # Graph methods.

    def label(self):
        return unicode(self)

class Connection:

    "A connection between textual fragments."

    def __init__(self, similarity, fragments):

        """
        Initialise a connection with the given 'similarity' and 'fragments'
        involved.
        """

        # Permit initialisation using an empty list for later population,
        # testing the fragments otherwise.

        if fragments and len(fragments) != 2:
            raise ValueError, fragments

        self.similarity = similarity
        self.fragments = fragments

    def __cmp__(self, other):

        """
        Compare this connection to another, using the overall measure of
        fragment similarity between the connected fragments as the primary
        value for comparison.
        """

        key = self.measure(), self.similarity
        other_key = other.measure(), other.similarity
        return cmp(key, other_key)

    def __hash__(self):

        "Permit the connection to be used as a dictionary key."

        return hash(tuple(map(hash, self.fragments)))

    def __nonzero__(self):

        "Return the truth or non-emptiness of the connection."

        return bool(self.fragments)

    def __repr__(self):
        return "Connection(%r, %r)" % self.as_tuple()

    def as_tuple(self):
        return (self.similarity, self.fragments)

    # Fragment detail methods.

    def measure(self):

        """
        Return an overall similarity measure using the full similarity details.
        """

        vectors = get_term_vectors(self.fragments)
        return get_term_vector_similarity(vectors, self.similarity)

    def relation(self, fragment):

        "Return the relation for the given 'fragment' in this connection."

        i = self.fragments.index(fragment)
        return self.fragments[1 - i]

    # Graph methods.

    def label(self):

        "Return a graph label, this being the overall similarity measure."

        return self.measure()

class Fragment:

    "A fragment of text from a transcript."

    def __init__(self, source, category, words=None, text=None):

        """
        Initialise a fragment from 'source', the nominated 'category', and a
        collection of corresponding 'words'. Any original 'text' may be set or
        instead committed later using the 'commit_text' method.
        """

        self.source = source
        self.category = category
        self.words = words or []
        self.text = text
        self.vector = None

    def __cmp__(self, other):

        """
        Compare this fragment to 'other' using the origin details of the
        fragment. This is used to order the fragments chronologically within
        source transcripts.
        """

        return cmp(self.source, other.source)

    def __contains__(self, other):

        "Match 'other' to the terms in this fragment."

        return other in self.words and other or None

    def __hash__(self):

        "Permit the fragment to be used as a dictionary key."

        return hash(self.source)

    def __nonzero__(self):

        "Return the truth or non-emptiness of the fragment."

        return bool(self.words)

    def __repr__(self):
        return "Fragment(%r, %r, %r, %r)" % self.as_tuple()

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        return unicode(self.source)

    def as_tuple(self):
        return (self.source, self.category, self.words, self.text)

    def commit_text(self):

        "Define the textual summary of the fragment."

        self.text = text_from_words(self.words)

    def get_text(self):

        "Return a recomputed textual summary from the words."

        return text_from_words(self.words)

    # Similarity methods.

    def word_frequencies(self):

        "Return a mapping of words to frequencies."

        d = CountingDict()

        for word in self.words:
            d[word] += 1

        return d

    def get_term_vector(self, frequencies=True):

        "Return a vector containing term weights."

        # Employ term frequencies as weights if requested.

        if frequencies:
            d = self.word_frequencies()

        # Otherwise, define the presence of terms.

        else:
            d = {}
            for word in self.words:
                d[word] = 1

        return d

    def set_term_vector(self, vector):
        self.vector = vector

    # Graph methods.

    def label(self):
        return unicode(self)

class Source:

    "A fragment source."

    def __init__(self, filename, start, end):

        """
        Initialise a source with the given 'filename' and 'start' and 'end'
        timings.
        """

        self.filename = os.path.split(filename)[-1]
        self.start = start
        self.end = end

    def __cmp__(self, other):

        "Compare this source to 'other'."

        key = self.as_tuple()
        other_key = other.as_tuple()
        return cmp(key, other_key)

    def __hash__(self):

        "Permit the source to be used as a dictionary key."

        return hash(self.as_tuple())

    def __repr__(self):
        return "Source(%r, %r, %r)" % self.as_tuple()

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        return u"%s:%s-%s" % self.as_tuple()

    def as_tuple(self):
        return (self.filename, self.start, self.end)

    def participant(self):

        "Return the specific participant."

        m = re.match(r"(A\d*)", self.filename)
        if m:
            return m.group()
        else:
            return self.filename

    # Graph methods.

    def label(self):
        return unicode(self)

class Term:

    "A simple tagged term."

    def __init__(self, word, tag=None, normalised=None):

        """
        Initialise the term with the actual 'word', optional part-of-speech
        'tag' and 'normalised' form (lemma).
        """

        self.word = word
        self.tag = tag
        self.normalised = normalised

    def __cmp__(self, other):

        "Compare with 'other' using the normalised forms if possible."

        if self.normalised and isinstance(other, Term) and other.normalised:
            return cmp(self.normalised, other.normalised)
        else:
            return cmp(unicode(self), unicode(other))

    def __hash__(self):
        return hash(self.normalised or unicode(self))

    def __repr__(self):
        return "Term(%r, %r, %r)" % (self.word, self.tag, self.normalised)

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        return self.word

# Fragment collection operations.

def commit_text(fragments):

    "Preserve the original text in the 'fragments'."

    for fragment in fragments:
        fragment.commit_text()

def compare_fragments(fragments, terms_to_fragments=None):

    """
    Compare 'fragments' with each other, returning a list of connections
    sorted by the similarity measure. The 'terms_to_fragments' mapping, if
    provided, is used to optimise the fragment pairing process.
    """

    connections = []

    # Compare the fragment pairs.

    for pair in get_fragment_pairs(fragments, terms_to_fragments):
        vectors = get_term_vectors(pair)
        similarity = combine_term_vectors(vectors)

        # Only record connections when some similarity exists.

        if similarity:
            connections.append(Connection(similarity, pair))

    connections.sort(key=lambda c: c.measure())
    return connections

def fix_category_names(fragments, category_map):

    "Fix the category names in 'fragments' using the given 'category_map'."

    for fragment in fragments:
        fix = category_map.get(fragment.category.parent)
        if fix:
            fragment.category.parent = fix

def get_all_words(fragments):

    "Return a sorted list of unique words."

    s = set()

    for fragment in fragments:
        s.update(fragment.words)

    l = list(s)
    l.sort()
    return l

def get_fragment_pairs(fragments, terms_to_fragments=None):

    "Get pairs of 'fragments' to compare."

    if terms_to_fragments:
        pairs = []

        for f1 in fragments:
            others = set()

            # For each term, find fragments containing that term.

            for term in set(f1.words):
                others_for_term = terms_to_fragments.get(term)

                # Ignore terms without fragments.

                if not others_for_term:
                    continue

                # Obtain fragments that have not already been paired.

                for f2 in others_for_term:
                    if f1.source < f2.source:
                        others.add(f2)

            for f2 in others:
                pairs.append((f1, f2))

        return pairs
    else:
        return list(combinations(fragments, 2))

def get_fragment_terms(fragments, key_function=None):

    """
    Return a dictionary mapping fragments to terms. If 'key_function' is
    specified, call this function on each fragment to yield a suitable
    dictionary key instead of the fragment.
    """

    fn = key_function or (lambda fragment: fragment)
    d = defaultdict(list)

    for fragment in fragments:
        d[fn(fragment)] += fragment.words

    return d

def get_term_vectors(fragments):

    "Return the term vectors for 'fragments'."

    return map(lambda f: f.vector, fragments)

def inverse_document_frequencies(frequencies, numdocs):

    "Return the inverse document frequencies for 'frequencies' given 'numdocs'."

    d = {}

    for word, freq in frequencies.items():
        d[word] = log(float(numdocs) / (1 + freq), 10)

    return d

def process_fragments(fragments, processes):

    """
    Process 'fragments' using the given 'processes', redefining the words (or
    terms) in the fragments.
    """

    for fragment in fragments:
        for process in processes:
            fragment.words = process(fragment.words)

def process_term_vectors(fragments, frequencies=True, mapping=None):

    """
    Process term vectors from 'fragments', employing term frequencies if the
    'frequencies' indicator is set to a true value, and employing any 'mapping'
    to scale term weights.
    """

    for fragment in fragments:
        vector = fragment.get_term_vector(frequencies)
        scale_term_vector(vector, mapping)
        fragment.set_term_vector(vector)

def recompute_connections(connections):

    "Recompute the similarity details of the given 'connections'."

    for connection in connections:
        vectors = get_term_vectors(connection.fragments)
        connection.similarity = combine_term_vectors(vectors)

def scale_term_vector(vector, mapping=None):

    "Scale the 'vector' using a term 'mapping' to weights."

    if mapping:
        for word, weight in vector.items():
            vector[word] = weight * (mapping.get(word) or 1)

def word_document_frequencies(fragments):

    "Return document frequencies for words from the 'fragments'."

    d = CountingDict()

    for fragment in fragments:
        for word in fragment.word_frequencies().keys():
            d[word] += 1

    return d

def word_frequencies(fragments):

    "Merge word frequencies from the given 'fragments'."

    d = CountingDict()

    for fragment in fragments:
        for word, occurrences in fragment.word_frequencies().items():
            d[word] += occurrences

    return d

# Term catalogues.

def get_common_terms(entity_terms):

    "Return a distribution mapping terms to common entities."

    d = defaultdict(set)

    for entity, terms in entity_terms.items():
        for term in terms:
            d[term].add(entity)

    return d

# vim: tabstop=4 expandtab shiftwidth=4
