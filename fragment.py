#!/usr/bin/env python
# -*- coding: utf-8

"""
Collect words into the identified fragments, reducing the words to only those
of importance. Define fragment similarity by identifying common terms,
potentially weighting some terms as being more significant than others.
"""

from inputs import get_fragments_from_files, \
                   fill_categorised_fragments, get_categorised_fragments, \
                   populate_fragments

from objects import Category, Fragment, \
                    commit_text, \
                    compare_fragments, \
                    get_all_words, \
                    get_category_terms, \
                    get_fragment_terms, \
                    get_related_fragments, \
                    inverse_document_frequencies, \
                    word_document_frequencies, word_frequencies

from analysis import process_fragment_tokens, \
                     lower_word, stem_word

from grouping import group_words

from stopwords import filter_terms_by_pos

from text import normalise_accents

import graph
import outputs

from collections import defaultdict
import sys

# Fragment processing.

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

    allow_uncategorised = "--all-fragments" in sys.argv

    # Derive filenames for output files.

    out = outputs.Output(outdir)
    outfile = out.filename

    fragments = get_fragments_from_files(filenames)

    # Discard empty fragments.

    fragments = filter(None, fragments)

    # Discard uncategorised fragments.

    if not allow_uncategorised:
        fragments = filter(lambda f: f.category, fragments)

    # Output words.

    all_words = get_all_words(fragments)
    outputs.show_all_words(all_words, outfile("words.txt"))

    # Tidy up the data.

    process_fragments(fragments, [normalise_accents])
    commit_text(fragments)

    # Perform some processes on the words:

    # Part-of-speech tagging.
    # Normalisation involving stemming and lower-casing of words.

    process_fragment_tokens(fragments, [stem_word, lower_word])

    # Grouping of words into terms.
    # Filtering of stop words by selecting certain kinds of words (nouns, verbs,
    # adjectives).

    process_fragments(fragments, [group_words, filter_terms_by_pos])

    # Emit the fragments for inspection.

    outputs.show_fragments(fragments, outfile("fragments.txt"))

    # Get terms used by each category for inspection.

    category_terms = get_category_terms(fragments)
    outputs.show_category_terms(category_terms, outfile("terms.txt"))

    # Get common terms (common between categories).

    common_category_terms = get_common_terms(category_terms)
    outputs.show_common_terms(common_category_terms, outfile("term_categories.txt"))

    # Get common terms (common between fragments).

    fragment_terms = get_fragment_terms(fragments)

    common_fragment_terms = get_common_terms(fragment_terms)
    outputs.show_common_terms(common_fragment_terms, outfile("term_fragments.txt"))

    # Get term/word frequencies.

    frequencies = word_frequencies(fragments)
    outputs.show_frequencies(frequencies, outfile("term_frequencies.txt"))

    doc_frequencies = word_document_frequencies(fragments)
    outputs.show_frequencies(doc_frequencies, outfile("term_doc_frequencies.txt"))

    inv_doc_frequencies = inverse_document_frequencies(doc_frequencies, len(fragments))
    outputs.show_frequencies(inv_doc_frequencies, outfile("term_inv_doc_frequencies.txt"))

    # Determine fragment similarity by taking the processed words and comparing
    # fragments.

    connections = compare_fragments(fragments, idf=inv_doc_frequencies)

    # Emit the connections for inspection.

    outputs.show_connections(connections, outfile("connections.txt"))

    related = get_related_fragments(connections)
    outputs.show_related_fragments(related, outfile("relations.txt"))

    # Produce a graph where each fragment is a node and the similarity (where
    # non-zero) is an edge linking the fragments.

    graph.write_graph(fragments, connections, outfile("graph.dot"))

# vim: tabstop=4 expandtab shiftwidth=4
