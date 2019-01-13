#!/usr/bin/env python
# -*- coding: utf-8

"""
Textual abstractions.
"""

from collections import defaultdict
from itertools import combinations
from math import log
from text import is_punctuation

class Category:

    "A complete category description featuring a parent and child category."

    def __init__(self, parent, category):
        self.parent = parent
        self.category = category

    def __cmp__(self, other):
        return cmp(self.as_tuple(), other.as_tuple())

    def __hash__(self):
        return hash(self.as_tuple())

    def __repr__(self):
        return "Category(%r, %r)" % self.as_tuple()

    def __str__(self):
        return "%s-%s" % self.as_tuple()

    def __unicode__(self):
        return str(self)

    def as_tuple(self):
        return (self.parent, self.category)

    # Graph methods.

    def label(self):
        return str(self)

class Connection:

    "A connection between textual fragments."

    def __init__(self, similarity, fragments):

        """
        Initialise a connection with the given 'similarity' and 'fragments'
        involved.
        """

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

        return sum(self.similarity.values())

    def relations(self):

        """
        Return the relations for each fragment in this connection, using the
        form (fragment, related fragments) for each fragment.
        """

        return get_fragment_relations(self.fragments)

    # Graph methods.

    def label(self):

        "Return a graph label, this being the overall similarity measure."

        return self.measure()

class Fragment:

    "A fragment of text from a transcript."

    def __init__(self, source, start, end, category, words=None, text=None):

        """
        Initialise a fragment from 'source' with the given 'start' and 'end'
        timings, the nominated 'category', and a collection of corresponding
        'words'. Any original 'text' may be set or instead committed later using
        the 'commit_text' method.
        """

        self.source = source
        self.start = start
        self.end = end
        self.category = category
        self.words = words or []
        self.text = text

    def __cmp__(self, other):

        """
        Compare this fragment to 'other' using the origin details of the
        fragment.
        """

        key = (self.source, self.start)
        other_key = (other.source, other.start)
        return cmp(key, other_key)

    def __contains__(self, other):

        "Match 'other' to the terms in this fragment."

        if isinstance(other, Term):
            return other.search(self)
        else:
            return other in self.words and other or None

    def __hash__(self):

        "Permit the fragment to be used as a dictionary key."

        return hash((self.source, self.start, self.end, self.category))

    def __nonzero__(self):

        "Return the truth or non-emptiness of the fragment."

        return bool(self.words)

    def __repr__(self):
        return "Fragment(%r, %r, %r, %r, %r, %r)" % self.as_tuple()

    def as_tuple(self):
        return (self.source, self.start, self.end, self.category, self.words, self.text)

    def commit_text(self):

        "Define the textual summary of the fragment."

        self.text = text_from_words(self.words)

    def get_text(self):

        "Return a recomputed textual summary from the words."

        return text_from_words(self.words)

    def original_words(self):

        "Return the originally-specified words for the terms in this fragment."

        l = []
        for word in self.words:
            l.append(unicode(word))
        return l

    # Similarity methods.

    def intersection(self, other):

        "Provide the intersection of terms in this and the 'other' fragment."

        l = []
        for word in self.words:
            if word in other:
                l.append(word)
        return l

    def union(self, other):

        "Provide the union of terms in this and the 'other' fragment."

        return self.words + other.words

    def word_frequencies(self):

        "Return a mapping of original words to frequencies."

        d = CountingDict()
        for word in self.original_words():
            d[word] += 1
        return d

    # Graph methods.

    def label(self):
        return "%s:%s-%s" % (self.source, self.start, self.end)

class Term:

    "A word or term used in text."

    def __init__(self, word, forms=None):
        self.word = word
        self.forms = set(forms) or set([word])

    def __repr__(self):
        return "Term(%r)" % self.word

    def __str__(self):
        return self.word

    def __unicode__(self):
        return self.word

    def __cmp__(self, other):

        "Compare this term to 'other'."

        # Try and find an intersection of the forms defined for this term and
        # for the other object. If there is an intersection, return equality.

        if self.intersection(other):
            return 0

        # Without an intersection, just compare this term as a plain word.

        return cmp(self.word, other)

    def __nonzero__(self):
        return bool(self.forms)

    def intersection(self, other):

        "Provide the intersection of forms in this and the 'other' word or term."

        # With another term, obtain the intersection of the terms' forms.

        if isinstance(other, Term):
            return self.forms.intersection(other.forms)

        # Otherwise, look for the other object in this term's forms.

        if other in self.forms:
            return [other]
        else:
            return []

    def search(self, fragment):

        "Search for this term in 'fragment', returning this term if found."

        for word in fragment.words:
            if self.intersection(word):
                return self

        # Split up this term to search distinct words.

        for form in self.forms:
            if "_" not in form:
                continue
            if match_tokens(form.split("_"), fragment.original_words()):
                return self

        return None

class CountingDict(defaultdict):

    "A simple counting dictionary."

    def __init__(self):
        defaultdict.__init__(self, lambda: 0)

    def __repr__(self):
        l = []
        for key, value in self.items():
            l.append("%r: %r" % (key, value))
        return "{%s}" % ", ".join(l)

def match_tokens(tokens, words):

    "Match the given 'tokens' consecutively in the collection of 'words'."

    to_test = []

    for i, word in enumerate(words):
        if tokens[0] == word:
            to_test.append(i)

    for i in to_test:
        to_match = tokens[1:]
        for word in words[i+1:]:
            if word == to_match[0]:
                del to_match[0]
                if not to_match:
                    return True
            else:
                break

    return False

def scale_similarity(commonfreq, total=None, idf=None):

    """
    Using 'commonfreq' being a mapping from terms common to two fragments to
    their frequencies, and 'total' being the total frequency of terms in the
    fragments, return a list mapping terms to similarity measures scaled using
    'idf'.
    """

    if not total:
        total = 1

    d = {}

    for term, freq in commonfreq.items():

        # Convert the term to a suitable form for the IDF mapping.

        word = unicode(term)
        idf_for_term = idf and idf[term] or 1
        d[term] = float(freq) / total * idf_for_term

    return d

def text_from_words(words):

    "Join 'words' in order to produce a reasonable text string."

    if not words:
        return ""

    l = [words[0]]

    for word in words[1:]:
        if not is_punctuation(word):
            l.append(" ")
        l.append(word)

    return "".join(l)

# Fragment collection operations.

def commit_text(fragments):

    "Preserve the original text in the 'fragments'."

    for fragment in fragments:
        fragment.commit_text()

def compare_fragments(fragments, wf=False, idf=None):

    """
    Compare 'fragments' with each other, returning a list of connections
    sorted by the similarity measure.

    If 'wf' is a true value, use the word frequency distribution of each pair of
    fragments to scale term weights.

    If 'idf' is given, use this inverse document frequency distribution to scale
    term weights.
    """

    connections = []

    for f1, f2 in combinations(fragments, 2):
        t = (f1, f2)
        similarity = get_fragment_similarity(t, wf, idf)
        if similarity:
            connections.append(Connection(similarity, t))

    connections.sort(key=lambda c: c.measure())
    return connections

def get_category_terms(fragments):

    "Return a dictionary mapping categories to terms."

    d = defaultdict(list)

    for fragment in fragments:
        for word in fragment.words:
            d[fragment.category].append(word)

    return d

def get_fragment_relations(fragments):

    """
    Return the relations for each fragment in the given 'fragments' collection,
    using the form (fragment, related fragments) for each fragment.
    """

    l = []

    for i, fragment in enumerate(fragments):
        l.append((fragment, fragments[:i] + fragments[i+1:]))

    return l

def get_fragment_similarity(fragments, wf=False, idf=None):

    "Return the similarity of the given 'fragments'."

    d = CountingDict()

    # For each fragment, get the occurrences of terms in related fragments.

    for fragment, related in get_fragment_relations(fragments):
        for other in related:
            for word in fragment.intersection(other):

                # Employ the original word in any mapping.

                d[unicode(word)] += 1

    return scale_similarity(d, wf and sum(word_frequencies(fragments).values()) or None, idf)

def get_fragment_terms(fragments):

    "Return a dictionary mapping fragments to terms."

    d = {}

    for fragment in fragments:
        d[fragment] = fragment.words

    return d

def inverse_document_frequencies(frequencies, numdocs):

    "Return the inverse document frequencies for 'frequencies' given 'numdocs'."

    d = {}

    for word, freq in frequencies.items():
        d[word] = log(float(numdocs) / (1 + freq), 10)

    return d

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

def get_related_fragments(connections):

    """
    Using 'connections', obtain the fragments related to each fragment,
    returning a mapping from fragments to (measure, related fragment,
    similarity), where similarity is the full similarity result.
    """

    # Visit all connections and collect for each fragment all the related
    # fragments together with the similarity details between the principal
    # fragment and each related fragment.

    d = defaultdict(list)

    for connection in connections:

        # The computed measure is used to rank the related fragments. General
        # similarity details are also included in the data for eventual output.

        measure = connection.measure()
        similarity = connection.similarity

        # Obtain related fragments for this connection. There should only be
        # one, but the connection supports relationships between more than two
        # fragments in general.

        for fragment, relations in connection.relations():
            for relation in relations:
                d[fragment].append((measure, relation, similarity))

    return d

# vim: tabstop=4 expandtab shiftwidth=4
