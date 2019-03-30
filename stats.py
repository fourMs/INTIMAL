#!/usr/bin/env python
# -*- coding: utf-8

"""
Statistics generation for fragments.
"""

from objects import get_common_terms, \
                    get_fragment_categories, get_fragment_terms, \
                    inverse_document_frequencies, \
                    word_document_frequencies, word_frequencies

import outputs



# Processing and output functions.

def process_statistics(fragments, out):

    "Process 'fragments' to obtain statistics, registering output with 'out'."

    # Get fragments in each category.

    category_fragments = get_fragment_categories(fragments)

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

    out["category_fragments"] = category_fragments
    out["category_terms"] = category_terms
    out["common_category_terms"] = common_category_terms
    out["common_fragment_terms"] = common_fragment_terms
    out["frequencies"] = frequencies
    out["doc_frequencies"] = doc_frequencies
    out["inv_doc_frequencies"] = inv_doc_frequencies

def emit_statistics_output(out):

    "Using 'out', emit output data featuring statistical reports."

    outfile = out.filename

    # Emit term details for inspection.

    outputs.show_common_terms(out["category_fragments"], outfile("category_fragments.txt"), "\t")
    outputs.show_common_terms(out["category_fragments"], outfile("category_fragments_summary.txt"), summary=True)
    outputs.show_category_terms(out["category_terms"], outfile("terms.txt"))
    outputs.show_common_terms(out["common_category_terms"], outfile("term_categories.txt"))
    outputs.show_common_terms(out["common_fragment_terms"], outfile("term_fragments.txt"))
    outputs.show_frequencies(out["frequencies"], outfile("term_frequencies.txt"))
    outputs.show_frequencies(out["doc_frequencies"], outfile("term_doc_frequencies.txt"))
    outputs.show_frequencies(out["inv_doc_frequencies"], outfile("term_inv_doc_frequencies.txt"))

# vim: tabstop=4 expandtab shiftwidth=4
