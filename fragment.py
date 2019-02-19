#!/usr/bin/env python
# -*- coding: utf-8

"""
Collect words into the identified fragments, reducing the words to only those
of importance.

Define fragment similarity by identifying common terms, potentially weighting
some terms as being more significant than others.

Collect sorted relations between fragments according to different selection
criteria.

Produce reports and structured data describing the processed data.
"""

# Input and output.

from inputs import get_fragments_from_files, get_categorised_fragments, \
                   get_list_from_file, get_map_from_file, \
                   get_flag, get_option, get_options

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
                    recompute_connections, \
                    word_document_frequencies, word_frequencies

from related import get_related_fragments, \
                    get_related_fragment_selectors, \
                    related_fragment_selectors, \
                    select_related_fragments, \
                    sort_related_fragments

# Transformations on the words and text.

from analysis import process_fragment_tokens, \
                     lower_word, stem_word

from grouping import group_words

from serialised import get_serialised_connections, get_serialised_fragments

from stopwords import POSFilter

from text import normalise_accents, remove_punctuation_from_words

from wordlist import get_wordlist_from_file



# The input data processing workflow.

def process_input_data(filenames, config, out):

    """
    Process data from 'filenames', using 'config' to adjust the processing,
    registering output data with 'out'.
    """

    fragments = get_fragments_from_files(filenames)

    # Discard empty fragments.

    fragments = filter(None, fragments)

    # Discard uncategorised fragments.

    if not config.get("all_fragments"):
        fragments = filter(lambda f: f.category and f.category.complete(), fragments)

    # Fix fragment categories.

    if config.get("category_map"):
        fix_category_names(fragments, config.get("category_map"))

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

    process_fragments(fragments, [group_words,
                                  config.get("posfilter").filter_words])

    # Selection of desired words.

    if config.get("wordlist"):
        process_fragments(fragments, [config.get("wordlist").filter_words])

    # Register some output data.

    out["all_words"] = all_words
    out["fragments"] = fragments

    return fragments

def process_statistics(fragments, out):

    "Process 'fragments' to obtain statistics, registering output with 'out'."

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

    # Register some output data.

    out["category_terms"] = category_terms
    out["common_category_terms"] = common_category_terms
    out["common_fragment_terms"] = common_fragment_terms
    out["frequencies"] = frequencies
    out["doc_frequencies"] = doc_frequencies
    out["inv_doc_frequencies"] = inv_doc_frequencies

def process_fragment_data(fragments, out):

    "Process 'fragments' to obtain connections, registering output with 'out'."

    process_statistics(fragments, out)

    # Determine fragment similarity by taking the processed words and comparing
    # fragments.

    connections = compare_fragments(fragments, idf=out["inv_doc_frequencies"],
                                    terms_to_fragments=out["common_fragment_terms"])

    # Register some output data.

    out["connections"] = connections

    return connections



# Restoration of serialised data.

def restore_fragments(out):

    "Restore fragments from an output file via 'out'."

    out["fragments"] = fragments = \
        get_serialised_fragments(outfile("fragments.txt"))

    return fragments

def restore_connections(fragments, out):

    "Using 'fragments', restore connections from an output file via 'out'."

    out["connections"] = connections = \
        get_serialised_connections(outfile("connections.txt"), fragments)

    # Recompute the similarities.

    recompute_connections(connections, out["inv_doc_frequencies"])

    return connections



# Relation processing.

def process_relations(connections, config, out):

    """
    Process 'connections' to obtain relations, using 'config' to adjust the
    processing, registering output with 'out'.
    """

    related = get_related_fragments(connections)

    # Impose an ordering on the related fragments.

    sort_related_fragments(related)

    # Only restrict the related fragments if requested.

    if not config.has_key("select"):
        return related

    num = config.get("num_related_fragments")
    all_related = []

    # For each set of selection criteria, select appropriate fragments.

    for criteria in config.get("select"):

        # Obtain the functions from their names.

        names = criteria.split(",")
        selectors = get_related_fragment_selectors(names)

        # Select and store the related fragments.

        all_related.append((criteria, select_related_fragments(related, num, selectors)))

    out["all_related"] = all_related

    return related



# Output data production.

def emit_basic_output(out):

    "Using 'out', emit basic output data featuring the processed input."

    outfile = out.filename

    # Emit the fragments for inspection and potential recovery.

    outputs.show_fragments(out["fragments"], outfile("fragments.txt"))

    # Emit the connection details for potential recovery.

    outputs.show_connections(out["connections"], outfile("connections.txt"), brief=True)

    # Emit details of all the different words originally encountered.

    outputs.show_all_words(out["all_words"], outfile("words.txt"))

def emit_statistics_output(out):

    "Using 'out', emit output data featuring statistical reports."

    outfile = out.filename

    # Emit term details for inspection.

    outputs.show_category_terms(out["category_terms"], outfile("terms.txt"))
    outputs.show_common_terms(out["common_category_terms"], outfile("term_categories.txt"))
    outputs.show_common_terms(out["common_fragment_terms"], outfile("term_fragments.txt"))
    outputs.show_frequencies(out["frequencies"], outfile("term_frequencies.txt"))
    outputs.show_frequencies(out["doc_frequencies"], outfile("term_doc_frequencies.txt"))
    outputs.show_frequencies(out["inv_doc_frequencies"], outfile("term_inv_doc_frequencies.txt"))

def emit_verbose_output(out):

    "Using 'out', emit output data featuring verbose details."

    outfile = out.filename

    # Emit the connections for inspection.

    outputs.show_connections(out["connections"], outfile("connections_verbose.txt"))

def emit_relation_output(out):

    "Using 'out', emit relation output."

    outfile = out.filename
    datasets = out.get("all_related")

    if not datasets:
        return

    # Emit related data.

    for criteria, dataset in datasets:
        outputs.show_related_fragments(dataset, outfile(criteria))

    outputs.write_fragment_data(datasets, outfile("data"))



# Help text for program invocation.

progname = os.path.split(sys.argv[0])[-1]

related_fragment_selectors_list = list(related_fragment_selectors)
related_fragment_selectors_list.sort()

related_fragment_selectors_text = "\n".join(related_fragment_selectors_list)

helptext = """\
Usage: %s [ <options> ] <output directory> [ <input file>... ]

An output directory name is always needed. Initially, a collection of text and
tiers filenames for reading are also needed. Subsequently, this collection of
filenames can be omitted, and the previously-processed data will be loaded
instead.

Input file processing options:

--all-fragments         Process all fragments including uncategorised ones

--category-map <filename>
                        Change categories according to the mapping defined in
                        the indicated file

--pos-tags <filename>   Preserve only words with the part-of-speech tags found
                        in the indicated file

--word-list <filename>  Preserve only words found in the indicated file, these
                        being the root forms of word families (for example,
                        general verbs instead of conjugations)

Output options:

--num-related <number>  Indicate the maximum number of related fragments to be
                        produced for each fragment

--select <criteria>     Select related fragments using the given criteria, these
                        being a comma-separated list of functions, described
                        below

--stats                 Produce full output featuring statistical reports

--verbose               Produce verbose output describing the data

Related fragments can be selected by combining criteria specified using a list
of functions chosen from the following:

%s

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
""" % (progname, related_fragment_selectors_text)



# Main program.

if __name__ == "__main__":

    config = {}

    config["all_fragments"] = get_flag("--all-fragments")
    config["category_map"] = get_map_from_file(get_option("--category-map"))
    config["num_related_fragments"] = get_option("--num-related", 4, 4, int)
    config["posfilter"] = POSFilter(get_list_from_file(get_option("--pos-tags")))
    config["select"] = get_options("--select")
    config["wordlist"] = get_wordlist_from_file(get_option("--word-list"))

    statistics_output = get_flag("--stats")
    verbose_output = get_flag("--verbose")

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

    # Either restore serialised data.

    if restore:
        fragments = restore_fragments(out)
        process_statistics(fragments, out)
        connections = restore_connections(fragments, out)

    # Or process input data.

    else:
        fragments = process_input_data(filenames, config, out)
        connections = process_fragment_data(fragments, out)

        # Emit basic output to serialise the processed data.

        emit_basic_output(out)

    # Process relation data.

    process_relations(connections, config, out)

    # Emit output.

    if statistics_output:
        emit_statistics_output(out)

    if verbose_output:
        emit_verbose_output(out)

    emit_relation_output(out)

# vim: tabstop=4 expandtab shiftwidth=4
