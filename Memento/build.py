#!/usr/bin/env python2.7
# -*- coding: utf-8

"""
Building of a processed data set for further processing.

Copyright (C) 2018, 2019 University of Oslo

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.

----

Collect words into the identified fragments, reducing the words to only those
of importance.

Define fragment similarity by identifying common terms, potentially weighting
some terms as being more significant than others.

Produce reports describing the input data.
"""

# Input and output.

from inputs import get_fragments_from_files, \
                   get_list_from_file, get_map_from_file, \
                   get_flag, get_option

import outputs

import os, sys

# Abstractions and relation processing.

from objects import commit_text, \
                    compare_fragments, \
                    fix_category_names, \
                    get_all_words, \
                    get_common_terms, get_fragment_terms, \
                    process_fragments, \
                    process_term_vectors

# Transformations on the words and text.

from analysis import process_fragment_tokens, \
                     lower_word, stem_word

from grouping import group_words

from stopwords import POSFilter

from text import normalise_accents, remove_punctuation_from_words



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

    # Register some output data.

    out["all_words"] = all_words
    out["fragments"] = fragments

    return fragments

def process_fragment_data(fragments, config, out):

    """
    Process 'fragments' to obtain connections, using 'config' to adjust the
    processing, registering output with 'out'.
    """

    # Define the term vectors. This does not bother with term weight scaling or
    # other statistics-related operations since the objective is merely to
    # establish related fragments for further inspection.

    process_term_vectors(fragments)

    # Get common terms (common between fragments).

    fragment_terms = get_fragment_terms(fragments)
    common_fragment_terms = get_common_terms(fragment_terms)

    # Determine fragment similarity by taking the processed words and comparing
    # fragments.

    connections = compare_fragments(fragments,
                                    terms_to_fragments=common_fragment_terms)

    # Register some output data.

    out["connections"] = connections

    return connections



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

def emit_verbose_output(out):

    "Using 'out', emit output data featuring verbose details."

    outfile = out.filename

    # Emit the connections for inspection.

    outputs.show_connections(out["connections"], outfile("connections_verbose.txt"))



# Help text for program invocation.

progname = os.path.split(sys.argv[0])[-1]

helptext = """\
Usage: %s [ <options> ] <output directory> <input file>...

An output directory name is needed along with a collection of text and tiers
filenames for reading.

Input file processing options:

--all-fragments         Process all fragments including uncategorised ones

--category-map <filename>
                        Change categories according to the mapping defined in
                        the indicated file

--pos-tags <filename>   Preserve only words with the part-of-speech tags found
                        in the indicated file

Output options:

--verbose               Produce verbose output describing the data

The output directory will be populated with files containing the following:

 * fragments
 * connections
 * all words from fragments

If --verbose is indicated, a verbose report of the connections will be produced.
""" % progname



# Main program.

if __name__ == "__main__":

    # Show the help message if requested.

    if get_flag("--help"):
        print >>sys.stderr, helptext
        sys.exit(0)

    config = {}

    config["all_fragments"] = get_flag("--all-fragments")
    config["category_map"] = get_map_from_file(get_option("--category-map"))
    config["posfilter"] = POSFilter(get_list_from_file(get_option("--pos-tags")))

    verbose_output = get_flag("--verbose")

    # Obtain filenames.

    try:
        outdir = sys.argv[1]
        filenames = sys.argv[2:]
        need_at_least_one_filename = filenames[0]

    # Show the help message and exit if the arguments are incorrect.

    except (IndexError, ValueError):
        print >>sys.stderr, helptext
        sys.exit(1)

    # Derive filenames for output files.

    out = outputs.Output(outdir)
    outfile = out.filename

    # Process input data.

    fragments = process_input_data(filenames, config, out)
    connections = process_fragment_data(fragments, config, out)

    # Emit basic output to serialise the processed data.

    emit_basic_output(out)

    if verbose_output:
        emit_verbose_output(out)

# vim: tabstop=4 expandtab shiftwidth=4
