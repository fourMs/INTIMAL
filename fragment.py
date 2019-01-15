#!/usr/bin/env python
# -*- coding: utf-8

"""
Collect words into the identified fragments, reducing the words to only those
of importance. Define fragment similarity by identifying common terms,
potentially weighting some terms as being more significant than others.
Produce a graph describing the fragments and their relationships.

Using a visualisation tool to show the graph has limited benefit. The
relationships between pairs of fragments are most important in this application.
However, a layout algorithm will attempt to reconcile the demands made by each
relationship simultaneously. Consequently, two fragments that have a high
similarity may be pulled apart by the relationships such fragments have with
others.
"""

from inputs import get_categorised_fragments, populate_fragments

from objects import Category, Fragment, \
                    commit_text, compare_fragments, \
                    get_category_terms, get_fragment_terms, \
                    get_related_fragments, \
                    inverse_document_frequencies, \
                    word_document_frequencies, word_frequencies

from analysis import process_fragment_tokens, \
                     lower_word, stem_word

from graph import write_graph

from grouping import group_words

from stopwords import no_stop_words

from text import lower, normalise_accents, remove_punctuation, only_words

from collections import defaultdict
from os import mkdir
from os.path import isdir, join
from xml.dom.minidom import parse
import codecs
import sys

# Fragment processing.

def discard_empty_fragments(fragments):

    "Return a list of non-empty instances from 'fragments'."

    l = []

    for fragment in fragments:
        if fragment:
            l.append(fragment)

    return l

def get_all_words(fragments):

    "Return a sorted list of unique words."

    s = set()

    for fragment in fragments:
        s.update(fragment.words)

    l = list(s)
    l.sort()
    return l

def process_fragments(fragments, processes):

    """
    Process 'fragments' using the given 'processes', redefining the words (or
    terms) in the fragments.
    """

    for fragment in fragments:
        for process in processes:
            fragment.words = process(fragment.words)

# Term catalogues.

def get_common_terms(entity_terms):

    "Return a distribution mapping terms to common entities."

    d = defaultdict(set)

    for entity, terms in entity_terms.items():
        for term in terms:
            d[term].add(entity)

    return d

# Comparison functions.

def cmp_value_lengths(a, b):
    acat = len(a[1])
    bcat = len(b[1])
    return cmp(acat, bcat)

def cmp_values(a, b):
    return cmp(a[1], b[1])

# Output conversion.

def show_all_words(words, filename):

    "Show 'words' in 'filename'."

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for word in words:
            print >>out, word
    finally:
        out.close()

def show_category_terms(category_terms, filename):

    """
    Show the 'category_terms' mapping in 'filename', with each correspondence in
    the mapping being formatted as the category followed by each distinct term
    associated with the category.
    """

    l = category_terms.items()
    l.sort()
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for category, terms in l:
            terms = list(set(terms))
            terms.sort()
            print >>out, category
            for term in terms:
                print >>out, unicode(term)
            print >>out
    finally:
        out.close()

def show_common_terms(common_terms, filename):

    """
    Show 'common_terms' in 'filename', this illustrating each term together with
    the entities (categories or fragments) in which it appears.
    """

    # Sort the terms and entities by increasing number of entities.

    l = common_terms.items()
    l.sort(cmp=cmp_value_lengths)

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for term, entities in l:
            print >>out, unicode(term), ",".join(map(lambda e: e.label(), entities))
    finally:
        out.close()

def show_connections(connections, filename):

    "Write a report of 'connections' to 'filename'."

    connections.sort(key=lambda x: x.measure())
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for connection in connections:
            for term, weight in connection.similarity.items():
                print >>out, unicode(term), weight,
            print >>out
            for fragment in connection.fragments:
                print >>out, fragment.text
            print >>out
    finally:
        out.close()

def show_fragments(fragments, filename):

    "Write the textual representation of 'fragments' to 'filename'."

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for fragment in fragments:
            print >>out, fragment
    finally:
        out.close()

def show_frequencies(frequencies, filename):

    "Write the mapping of term 'frequencies' to 'filename'."

    l = frequencies.items()
    l.sort(cmp=cmp_values)
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for term, occurrences in l:
            print >>out, unicode(term), occurrences
    finally:
        out.close()

def show_related_fragments(related, filename, shown_relations=5):

    """
    Show the 'related' fragments: for each fragment, show the related fragments
    via the connections, writing the results to 'filename'.
    """

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for fragment, relations in related.items():

            # Show the related fragments in descending order of similarity.

            relations.sort(reverse=True)

            # Show the principal fragment details.

            print >>out, "  Id:", fragment.source, fragment.start, fragment.end
            print >>out, "Text:", fragment.text
            print >>out

            # For each related fragment, show details including the similarity
            # information.

            for measure, relation, similarity in relations[:shown_relations]:

                print >>out, "  Id:", relation.source, relation.start, relation.end
                print >>out, " Sim: %.2f" % measure,

                for term, score in similarity.items():
                    print >>out, "%s (%.2f)" % (unicode(term), score),

                print >>out
                print >>out, "Text:", relation.text
                print >>out

            if len(relations) > shown_relations:
                print >>out, "%d related fragments not shown." % (len(relations) - shown_relations)

            print >>out, "----"
            print >>out
    finally:
        out.close()

def ensure_directory(name):
    if not isdir(name):
        mkdir(name)

# Define the forms of filenames providing data.

datatypes = ["Text", "Tiers"]

def get_input_details(filename):

    """
    Return for 'filename' a tuple of the form (data type, basename). If the
    filename does not identify one of the recognised data types, return None.
    """

    for datatype in datatypes:
        if datatype in filename:
            return (datatype, filename.rsplit("_", 1)[0])

    return None

def get_input_filenames(args):

    """
    Process the filenames in 'args', identifying groups of filenames to be
    processed together. The result is a mapping from each filename prefix to the
    corresponding group. The group is a mapping from each data type to the
    corresponding filename providing the data.
    """

    d = defaultdict(set)

    # Produce a mapping from prefix to (data type, filename).

    for arg in args:
        details = get_input_details(arg)

        # The filename must show signs of providing a recognised data type.

        if details:
            datatype, prefix = details
            d[prefix].add((datatype, arg))

    # Generate a list of (prefix, filename mapping) entries.

    l = []

    for prefix, filenames in d.items():

        # All the required data types must be supported by the files.

        if len(filenames) == len(datatypes):
            l.append((prefix, dict(filenames)))

    return l

helptext = """\
Need an output directory name plus a collection of text and tiers filenames for
reading. The output directory will be populated with files containing the
following:

 * fragments
 * connections
 * all words from fragments
 * category terms (terms found in each category)
 * common category terms (categories associated with each term)
 * common fragment terms (fragments associated with each term)
 * term frequencies
 * term document frequencies
 * term inverse document frequencies
 * fragments and related fragments
 * illustration graphs
"""

# Main program.

if __name__ == "__main__":

    # Obtain filenames.

    try:
        outdir = sys.argv[1]
        filenames = sys.argv[2:]
    except (IndexError, ValueError):
        print >>sys.stderr, helptext
        sys.exit(1)

    # Derive filenames for output files.

    ensure_directory(outdir)

    fragmentsfn = join(outdir, "fragments.txt")
    connectionsfn = join(outdir, "connections.txt")
    wordsfn = join(outdir, "words.txt")
    termsfn = join(outdir, "terms.txt")
    ctermsfn = join(outdir, "term_categories.txt")
    ftermsfn = join(outdir, "term_fragments.txt")
    termfreqfn = join(outdir, "term_frequencies.txt")
    termdocfreqfn = join(outdir, "term_doc_frequencies.txt")
    terminvdocfreqfn = join(outdir, "term_inv_doc_frequencies.txt")
    relationsfn = join(outdir, "relations.txt")
    dotfn = join(outdir, "graph.dot")

    # For each fragment defined by the tiers, collect corresponding words, producing
    # fragment objects.

    fragments = []

    for source, source_filenames in get_input_filenames(filenames):
        textfn = source_filenames["Text"]
        tiersfn = source_filenames["Tiers"]

        print tiersfn, textfn
        textdoc = parse(textfn)
        tiersdoc = parse(tiersfn)

        current_fragments = get_categorised_fragments(tiersdoc, source)
        populate_fragments(current_fragments, textdoc, source)

        fragments += current_fragments

    # Discard empty fragments.

    fragments = discard_empty_fragments(fragments)

    # Output words.

    all_words = get_all_words(fragments)
    show_all_words(all_words, wordsfn)

    # Tidy up the data.

    process_fragments(fragments, [normalise_accents])
    commit_text(fragments)

    # Perform some processes on the words:
    # Filtering of stop words.
    # Selection of dictionary words.
    # Part-of-speech tagging to select certain types of words (nouns and verbs).
    # Normalisation involving stemming, synonyms and semantic equivalences.

    process_fragment_tokens(fragments, [stem_word, lower_word])

    process_fragments(fragments, [group_words, only_words, no_stop_words])

    # Emit the fragments for inspection.

    show_fragments(fragments, fragmentsfn)

    # Get terms used by each category for inspection.

    category_terms = get_category_terms(fragments)
    show_category_terms(category_terms, termsfn)

    # Get common terms (common between categories).

    common_category_terms = get_common_terms(category_terms)
    show_common_terms(common_category_terms, ctermsfn)

    # Get common terms (common between fragments).

    fragment_terms = get_fragment_terms(fragments)

    common_fragment_terms = get_common_terms(fragment_terms)
    show_common_terms(common_fragment_terms, ftermsfn)

    # Get term/word frequencies.

    frequencies = word_frequencies(fragments)
    show_frequencies(frequencies, termfreqfn)

    doc_frequencies = word_document_frequencies(fragments)
    show_frequencies(doc_frequencies, termdocfreqfn)

    inv_doc_frequencies = inverse_document_frequencies(doc_frequencies, len(fragments))
    show_frequencies(inv_doc_frequencies, terminvdocfreqfn)

    # Determine fragment similarity by taking the processed words and comparing
    # fragments.

    connections = compare_fragments(fragments, idf=inv_doc_frequencies)

    # Emit the connections for inspection.

    show_connections(connections, connectionsfn)

    related = get_related_fragments(connections)
    show_related_fragments(related, relationsfn)

    # Produce a graph where each fragment is a node and the similarity (where
    # non-zero) is an edge linking the fragments.

    write_graph(fragments, connections, dotfn)

# vim: tabstop=4 expandtab shiftwidth=4
