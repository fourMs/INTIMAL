#!/usr/bin/env python
# -*- coding: utf-8

"""
Textual abstractions.
"""

from text import is_punctuation, match_tokens, text_from_words
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

        if len(fragments) != 2:
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

    def __repr__(self):
        return "Connection(%r, %r)" % self.as_tuple()

    def as_tuple(self):
        return (self.similarity, self.fragments)

    # Fragment detail methods.

    def measure(self):

        """
        Return an overall similarity measure using the full similarity details.
        """

        vectors = map(lambda f: f.term_vector(), self.fragments)
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

    term_vector = word_frequencies

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

    def __init__(self, word, tag=None):
        self.word = word
        self.tag = tag

    def __cmp__(self, other):
        return cmp(unicode(self), unicode(other))

    def __hash__(self):
        return hash(unicode(self))

    def __repr__(self):
        return "Term(%r, %r)" % (self.word, self.tag)

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        return self.word

# Fragment collection operations.

def commit_text(fragments):

    "Preserve the original text in the 'fragments'."

    for fragment in fragments:
        fragment.commit_text()

def compare_fragments(fragments, idf=None, terms_to_fragments=None):

    """
    Compare 'fragments' with each other, returning a list of connections
    sorted by the similarity measure.

    If 'idf' is given, use this inverse document frequency distribution to scale
    term weights.
    """

    connections = []

    # Compare the fragment pairs.

    for pair in get_fragment_pairs(fragments, terms_to_fragments):
        similarity = get_fragment_similarity(pair, idf)

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

def get_fragment_similarity(fragments, idf=None):

    """
    Obtain term vectors from 'fragments' and combine them to give an indication
    of similarity. Where 'idf' is given, use the inverse document frequency
    distribution to scale term weights.
    """

    tv = map(lambda f: f.term_vector(), fragments)
    return combine_term_vectors(tv, idf)

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

# Connection-related operations.

class ConnectedFragment:

    "A record of fragment relationships via connections."

    def __init__(self, fragment, connections):
        self.fragment = fragment
        self.connections = connections

    def __iter__(self):
        return RelatedFragments(self.fragment, self.connections)

class RelatedFragments:

    "A provider of related fragments from connections."

    def __init__(self, fragment, connections):
        self.fragment = fragment
        self.connection_iter = iter(connections)

    def next(self):

        "Return the next related fragment with its connection."

        while self.connection_iter:
            try:
                connection = self.connection_iter.next()
                return connection.relation(self.fragment), connection
            except StopIteration:
                self.connection_iter = None

        raise StopIteration

def get_related_fragments(connections):

    """
    Return a mapping from fragments to connections for the given 'connections'.
    """

    d = defaultdict(list)

    for connection in connections:
        for fragment in connection.fragments:
            d[fragment].append(connection)

    return d

def select_related_fragments(related, num, get_criteria):

    """
    For each fragment in the 'related' mapping, select related fragments having
    'num' different values, with each value obtained by calling the given
    'get_criteria' function.
    """

    d = defaultdict(list)

    for fragment, connections in related.items():
        values = set()
        values.add(get_criteria(fragment, values))

        # Obtain each related fragment, assessing it with the function.

        for related, connection in ConnectedFragment(fragment, connections):
            if len(values) >= num:
                break

            value = get_criteria(related, values)

            if value:
                d[fragment].append(connection)
                values.add(value)

    return d

def select_related_fragments_by_category(related, num):

    """
    For each fragment in the 'related' mapping, select related fragments from
    the same parent category but with 'num' different subcategories.
    """

    return select_related_fragments(related, num, get_distinct_subcategory)

def select_related_fragments_by_participant(related, num):

    """
    For each fragment in the 'related' mapping, select related fragments from
    'num' different participants.
    """

    return select_related_fragments(related, num, get_distinct_participant)

def sort_related_fragments(related):

    "Sort the 'related' fragments in descending order of similarity."

    for fragment, connections in related.items():
        connections.sort(key=lambda x: x.measure(), reverse=True)

# Fragment criteria helper functions.

def get_distinct_participant(fragment, values):

    """
    From 'fragment' select the participant, returning it if it is not in
    'values', returning None otherwise.
    """

    participant = fragment.source.participant()

    if participant not in values:
        return participant
    else:
        return None

def get_distinct_subcategory(fragment, values):

    """
    From 'fragment' select a category  subcategory, returning it if it is not in
    'values', returning None otherwise.
    """

    category = fragment.category
    first = values and list(values)[0] or None
    parent = first and first.parent or None

    # The parent category must match the existing categories.

    if not parent or category.parent == parent and category not in values:
        return category
    else:
        return None

# Term catalogues.

def get_common_terms(entity_terms):

    "Return a distribution mapping terms to common entities."

    d = defaultdict(set)

    for entity, terms in entity_terms.items():
        for term in terms:
            d[term].add(entity)

    return d

# vim: tabstop=4 expandtab shiftwidth=4
