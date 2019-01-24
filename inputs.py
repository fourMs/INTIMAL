#!/usr/bin/env python
# -*- coding: utf-8

"""
Fragment retrieval.
"""

from objects import Category, Fragment, Source

from collections import defaultdict
from xml.dom.minidom import parse

# XML node processing.

def textContent(n):
    l = []
    for t in n.childNodes:
        l.append(t.nodeValue)
    return "".join(l)

# XML document processing.

def fill_categorised_fragments(fragments):

    """
    Add fragments with null categories to the sorted 'fragments' where gaps in
    the timing exist between adjacent fragments.
    """

    l = []
    last = 0

    for fragment in fragments:
        start = fragment.source.start

        # Where the current fragment starts after the end of the last one,
        # introduce a null-category fragment.

        if fragment.source.start > last:
            l.append(Fragment(Source(fragment.source.filename, last, start),
                              None))

        l.append(fragment)
        last = fragment.source.end

    return l

def get_categorised_fragments(tiersdoc, source):

    "Using the 'tiersdoc' return a sorted list of fragments from 'source'."

    fragments = []

    # For each tier, get spans defining categorised fragments.

    for tier in tiersdoc.getElementsByTagName("TIER"):
        parent = tier.getAttribute("columns")

        # For each span, obtain the start and end timings plus the category.

        for span in tier.getElementsByTagName("span"):
            start = float(span.getAttribute("start"))
            end = float(span.getAttribute("end"))

            # The category is textual content within a subnode.

            for category in span.getElementsByTagName("v"):
                fragments.append(
                    Fragment(Source(source, start, end),
                             Category(parent, textContent(category))))
                break

    fragments.sort()
    return fragments

def populate_fragments(fragments, textdoc, source):

    "Populate the 'fragments' using information from 'textdoc' for 'source'."

    if not fragments:
        return

    it = iter(fragments)
    current = None

    # Obtain each word in turn. These must be sorted.

    for span in textdoc.getElementsByTagName("span"):
        start = float(span.getAttribute("start"))
        end = float(span.getAttribute("end"))

        # The word is textual content within a subnode.

        for word in span.getElementsByTagName("v"):
            text = textContent(word)
            break
        else:
            continue

        # Find the appropriate fragment, stopping if no more fragments remain.

        while current is None or start >= current.source.end:
            try:
                current = it.next()
            except StopIteration:
                return

        # Make sure each word is meant for the current fragment.

        if end > current.source.start and start < current.source.end:
            current.words.append(text)

# Input file handling.

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

def get_fragments_from_files(filenames):

    """
    Given the 'filenames' of files containing tier/fragment and textual data,
    return populated fragments.
    """

    # For each fragment defined by the tiers, collect corresponding words, producing
    # fragment objects.

    fragments = []

    for source, source_filenames in get_input_filenames(filenames):
        textfn = source_filenames["Text"]
        tiersfn = source_filenames["Tiers"]

        textdoc = parse(textfn)
        tiersdoc = parse(tiersfn)

        current_fragments = get_categorised_fragments(tiersdoc, source)
        current_fragments = fill_categorised_fragments(current_fragments)
        populate_fragments(current_fragments, textdoc, source)

        fragments += current_fragments

    return fragments

# vim: tabstop=4 expandtab shiftwidth=4
