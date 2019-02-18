#!/usr/bin/env python
# -*- coding: utf-8

"""
Collect words into the identified fragments, reducing the words to only those
of importance. Define fragment similarity by identifying common terms,
potentially weighting some terms as being more significant than others.
"""

# Input and output.

from inputs import get_fragments_from_files, get_categorised_fragments, \
                   get_list_from_file, get_map_from_file, \
                   get_option

import outputs

import os, sys

# Abstractions and relation processing.

from objects import commit_text, \
                    compare_fragments, \
                    fix_category_names, \
                    get_all_words, \
                    get_common_terms, get_fragment_terms, \
                    inverse_document_frequencies, \
                    process_fragments, \
                    word_document_frequencies, word_frequencies

from related import get_related_fragments, \
                    select_related_fragments_by_category, \
                    select_related_fragments_by_participant, \
                    sort_related_fragments

# Transformations on the words and text.

from analysis import process_fragment_tokens, \
                     lower_word, stem_word

from grouping import group_words

from serialised import get_serialised_connections, get_serialised_fragments

from stopwords import POSFilter

from text import normalise_accents, remove_punctuation_from_words

from wordlist import get_wordlist_from_file



# Help text for program invocation.

progname = os.path.split(sys.argv[0])[-1]

helptext = """\
Usage: %s [ <options> ] <output directory> [ <input file>... ]

Options:

--all-fragments         Process all fragments including uncategorised ones

--category-map <filename>
                        Change categories according to the mapping defined in
                        the indicated file

--num-related <number>  Indicate the maximum number of related fragments to be
                        produced for each fragment

--pos-tags <filename>   Preserve only words with the part-of-speech tags found
                        in the indicated file

--word-list <filename>  Preserve only words found in the indicated file, these
                        being the root forms of word families (for example,
                        general verbs instead of conjugations)

An output directory name is always needed. Initially, a collection of text and
tiers filenames for reading are also needed. Subsequently, this collection of
filenames can be omitted, and the previously-processed data will be loaded
instead.

The output directory will be populated with files containing the following:

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

The output directory will also contain a data subdirectory containing the
processed data in a structured form.
""" % progname

# Main program.

if __name__ == "__main__":

    all_fragments = get_option("--all-fragments", True, False)
    category_map = get_map_from_file(get_option("--category-map"))
    num_related_fragments = get_option("--num-related", 4, 4, int)
    posfilter = POSFilter(get_list_from_file(get_option("--pos-tags")))
    wordlist = get_wordlist_from_file(get_option("--word-list"))

    # Obtain filenames.

    try:
        outdir = sys.argv[1]
        filenames = sys.argv[2:]
    except (IndexError, ValueError):
        print >>sys.stderr, helptext
        sys.exit(1)

    # Detect the special case of using existing data.

    restore = not filenames

    # Derive filenames for output files.

    out = outputs.Output(outdir)
    outfile = out.filename

    outfile_connections = outfile("connections.txt")
    outfile_fragments = outfile("fragments.txt")

    # Either restore serialised data.

    if restore:
        fragments = get_serialised_fragments(outfile_fragments)
        connections = get_serialised_connections(outfile_connections, fragments)

    # Or process input data.

    else:
        fragments = get_fragments_from_files(filenames)

        # Discard empty fragments.

        fragments = filter(None, fragments)

        # Discard uncategorised fragments.

        if not all_fragments:
            fragments = filter(lambda f: f.category and f.category.complete(), fragments)

        # Fix fragment categories.

        if category_map:
            fix_category_names(fragments, category_map)

        # Obtain the raw input words.

        all_words = get_all_words(fragments)

        # Tidy up the data.

        process_fragments(fragments, [normalise_accents])
        commit_text(fragments)

        process_fragments(fragments, [remove_punctuation_from_words])

        # Perform some processes on the words:

        # Part-of-speech tagging.
        # Normalisation involving stemming and lower-casing of words.

        process_fragment_tokens(fragments, [stem_word, lower_word])

        # Grouping of words into terms.
        # Filtering of stop words by selecting certain kinds of words (for example,
        # nouns, verbs, adjectives).

        process_fragments(fragments, [group_words, posfilter.filter_words])

        # Selection of desired words.

        if wordlist:
            process_fragments(fragments, [wordlist.filter_words])

        # Get terms used by each category for inspection.

        category_terms = get_fragment_terms(fragments, lambda fragment:
                                                       fragment.category.parent)

        # Get common terms (common between categories).

        common_category_terms = get_common_terms(category_terms)

        # Get common terms (common between fragments).

        fragment_terms = get_fragment_terms(fragments)
        common_fragment_terms = get_common_terms(fragment_terms)

        # Get term/word frequencies.

        frequencies = word_frequencies(fragments)
        doc_frequencies = word_document_frequencies(fragments)
        inv_doc_frequencies = inverse_document_frequencies(doc_frequencies, len(fragments))

        # Determine fragment similarity by taking the processed words and comparing
        # fragments.

        connections = compare_fragments(fragments, idf=inv_doc_frequencies,
                                        terms_to_fragments=common_fragment_terms)

        # Emit the fragments for inspection and potential recovery.

        outputs.show_fragments(fragments, outfile_fragments)

        # Emit the connection details for potential recovery.

        outputs.show_connections(connections, outfile_connections, brief=True)

        # Emit term details for inspection.

        outputs.show_all_words(all_words, outfile("words.txt"))
        outputs.show_category_terms(category_terms, outfile("terms.txt"))
        outputs.show_common_terms(common_category_terms, outfile("term_categories.txt"))
        outputs.show_common_terms(common_fragment_terms, outfile("term_fragments.txt"))
        outputs.show_frequencies(frequencies, outfile("term_frequencies.txt"))
        outputs.show_frequencies(doc_frequencies, outfile("term_doc_frequencies.txt"))
        outputs.show_frequencies(inv_doc_frequencies, outfile("term_inv_doc_frequencies.txt"))

        # Emit the connections for inspection.

        outputs.show_connections(connections, outfile("connections_verbose.txt"))

    # Process data using the connections as input.

    related = get_related_fragments(connections)

    # Impose an ordering on the related fragments.

    sort_related_fragments(related)
    related_by_participant = select_related_fragments_by_participant(related, num_related_fragments)
    related_by_category = select_related_fragments_by_category(related, num_related_fragments)

    # Emit related data.

    outputs.show_related_fragments(related_by_participant, outfile("relations.txt"))
    outputs.show_related_fragments(related_by_category, outfile("relations_by_category.txt"))

    # Write related fragment data.

    datasets = [("translation", related_by_participant), ("rotation", related_by_category)]

    outputs.write_fragment_data(datasets, outfile("data"))

# vim: tabstop=4 expandtab shiftwidth=4
