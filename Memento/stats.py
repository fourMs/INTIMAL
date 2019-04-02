#!/usr/bin/env python
# -*- coding: utf-8

"""
Statistics generation for fragments.

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

    # Get category frequencies.

    category_doc_frequencies = dict(map(lambda i: (i[0], len(i[1])), category_fragments.items()))
    category_inv_doc_frequencies = inverse_document_frequencies(category_doc_frequencies, len(fragments))

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
    out["category_inv_doc_frequencies"] = category_inv_doc_frequencies

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
    outputs.show_frequencies(out["category_inv_doc_frequencies"], outfile("category_inv_doc_frequencies.txt"))
    outputs.show_category_terms(out["category_terms"], outfile("terms.txt"))
    outputs.show_common_terms(out["common_category_terms"], outfile("term_categories.txt"))
    outputs.show_common_terms(out["common_fragment_terms"], outfile("term_fragments.txt"))
    outputs.show_frequencies(out["frequencies"], outfile("term_frequencies.txt"))
    outputs.show_frequencies(out["doc_frequencies"], outfile("term_doc_frequencies.txt"))
    outputs.show_frequencies(out["inv_doc_frequencies"], outfile("term_inv_doc_frequencies.txt"))

# vim: tabstop=4 expandtab shiftwidth=4
