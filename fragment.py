#!/usr/bin/env python
# -*- coding: utf-8

"""
Collect words into the identified fragments, reducing the words to only those
of importance. Define fragment similarity by identifying common terms,
potentially weighting some terms as being more significant than others.
"""

from inputs import get_fragments_from_files, get_categorised_fragments, \
                   populate_fragments, \
                   get_list_from_file, get_map_from_file

from objects import commit_text, \
                    compare_fragments, \
                    fix_category_names, \
                    get_all_words, \
                    get_common_terms, get_fragment_terms, \
                    get_related_fragments, \
                    inverse_document_frequencies, \
                    process_fragments, \
                    select_related_fragments_by_category, \
                    select_related_fragments_by_participant, \
                    sort_related_fragments, \
                    word_document_frequencies, word_frequencies

from analysis import process_fragment_tokens, \
                     lower_word, stem_word

from grouping import group_words

from stopwords import POSFilter

from text import normalise_accents, remove_punctuation_from_words

from wordlist import get_wordlist_from_file

import outputs

import os, sys



# Help text for program invocation.

progname = os.path.split(sys.argv[0])[-1]

helptext = """\
Usage: %s [ <options> ] <output directory> <input file>...

Options:

--all-fragments         Process all fragments including uncategorised ones

--category-map <filename>
                        Change categories according to the mapping defined in
                        the indicated file

--pos-tags <filename>   Preserve only words with the part-of-speech tags found
                        in the indicated file

--word-list <filename>  Preserve only words found in the indicated file, these
                        being the root forms of word families (for example,
                        general verbs instead of conjugations)

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
""" % progname

def get_option(name, default=None, missing=None):

    """
    Return the value following the command option 'name' or 'default' if the
    option was found without a following value. Return 'missing' if the option
    was missing.
    """

    try:
        i = sys.argv.index(name)
        del sys.argv[i]
        value = sys.argv[i]
        del sys.argv[i]
        return value
    except IndexError:
        return default
    except ValueError:
        return missing

# Main program.

if __name__ == "__main__":

    all_fragments = get_option("--all-fragments", True, False)
    category_map = get_map_from_file(get_option("--category-map"))
    posfilter = POSFilter(get_list_from_file(get_option("--pos-tags")))
    wordlist = get_wordlist_from_file(get_option("--word-list"))

    # Obtain filenames.

    try:
        outdir = sys.argv[1]
        filenames = sys.argv[2:]
    except (IndexError, ValueError):
        print >>sys.stderr, helptext
        sys.exit(1)

    # Derive filenames for output files.

    out = outputs.Output(outdir)
    outfile = out.filename

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

    connections = compare_fragments(fragments, idf=inv_doc_frequencies)
    related = get_related_fragments(connections)

    # Impose an ordering on the related fragments.

    sort_related_fragments(related)
    related_by_participant = select_related_fragments_by_participant(related, 4)
    related_by_category = select_related_fragments_by_category(related, 4)

    # Emit the fragments for inspection.

    outputs.show_fragments(fragments, outfile("fragments.txt"))

    # Emit term details for inspection.

    outputs.show_all_words(all_words, outfile("words.txt"))
    outputs.show_category_terms(category_terms, outfile("terms.txt"))
    outputs.show_common_terms(common_category_terms, outfile("term_categories.txt"))
    outputs.show_common_terms(common_fragment_terms, outfile("term_fragments.txt"))
    outputs.show_frequencies(frequencies, outfile("term_frequencies.txt"))
    outputs.show_frequencies(doc_frequencies, outfile("term_doc_frequencies.txt"))
    outputs.show_frequencies(inv_doc_frequencies, outfile("term_inv_doc_frequencies.txt"))

    # Emit the connections for inspection.

    outputs.show_connections(connections, outfile("connections.txt"))
    outputs.show_related_fragments(related_by_participant, outfile("relations.txt"))
    outputs.show_related_fragments(related_by_category, outfile("relations_by_category.txt"))

    # Write related fragment data.

    datasets = [("translation", related_by_participant), ("rotation", related_by_category)]

    outputs.write_fragment_data(datasets, outfile("data"))

# vim: tabstop=4 expandtab shiftwidth=4
