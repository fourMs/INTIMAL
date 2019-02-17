#!/usr/bin/env python
# -*- coding: utf-8

"""
Fragment retrieval and other input processing.
"""

from objects import Category, Fragment, Source, Term

from collections import defaultdict
from xml.dom.minidom import parse
import codecs
import re
import sys

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

                # Normalise the category labels.

                parent = normalise(parent)
                category = normalise(textContent(category))

                fragments.append(
                    Fragment(Source(source, start, end),
                             Category(parent, category)))
                break

    fragments.sort()
    return fragments

def normalise(s):

    "Normalise capitalisation in 's'."

    l = []
    sep = False

    for part in re.split(r"(?<=[ _])([a-z])", s):
        if not sep:
            l.append(part)
        else:
            l.append(part.upper())
        sep = not sep

    return "".join(l)

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

# Serialised object processing.

def get_serialised_fragments(filename):

    "Return a list of fragments serialised in 'filename'."

    l = []

    f = codecs.open(filename, encoding="utf-8")
    try:
        current = Fragment(None, None)

        while True:

            # Read each line (xreadlines seems to return plain strings).

            line = f.readline()

            if not line:
                break

            # Remove trailing newlines and complete the current fragment if a
            # blank line is encountered.

            line = line.rstrip("\n")

            if not line:
                if current:
                    l.append(current)
                    current = Fragment(None, None)
                continue

            # Parse a record and modify the current fragment.

            key, value = line.split(": ", 1)
            key = key.lstrip()

            if key == "Category":
                current.category = get_serialised_category(value)
            elif key == "Source":
                current.source = get_serialised_source(value)
            elif key == "Terms":
                current.words = get_serialised_terms(value)
            elif key == "Text":
                current.text = value

        # Complete the current fragment.

        if current:
            l.append(current)

    finally:
        f.close()

    return l

def get_serialised_category(value):

    "Return a category from the given serialised 'value'."

    parent, category = value.split("-", 1)
    return Category(parent, category)

def get_serialised_source(value):

    "Return a source from the given serialised 'value'."

    source, period = value.split(":")
    start, end = period.split("-")
    return Source(source, float(start), float(end))

def get_serialised_terms(value):

    "Return a list of terms from the given serialised 'value'."

    l = []
    i = 0

    while i < len(value):
        term, i = get_term_from_summary(value, i)
        l.append(term)

        if i is None:
            break

        i += 1

    return l

def get_term_from_summary(value, pos=0):

    """
    Return a term from the given summary 'value', parsing from 'pos' if
    specified or from the start of 'value' otherwise.
    """

    text, pos = get_quoted_text(value, pos)

    # Term text by itself.

    if pos is None or value[pos] == " ":
        return Term(text), pos

    # Term with more details.

    else:
        tag, pos = get_unquoted_text(value, pos+1)

        # Term with tag only.

        if pos is None or value[pos] == " ":
            return Term(text, tag), pos

        # Term with tag and normalised form.

        else:
            normalised, pos = get_quoted_text(value, pos+1)
            return Term(text, tag, normalised), pos

def get_quoted_text(value, i):

    """
    Return the quoted text from 'value' starting at 'i', together with the
    position of the next separator.
    """

    if value[i] == '"':
        next_quote = value.find('"', i+1)
        text = value[i+1:next_quote]
        next_sep = next_quote + 1
        if next_sep < len(value):
            return text, next_sep
        else:
            return text, None

    return get_unquoted_text(value, i)

end_of_term_part = re.compile("[ :]")

def get_unquoted_text(value, i):

    """
    Return the text from 'value' starting at 'i', together with the position of
    the next separator.
    """

    match = end_of_term_part.search(value, i)
    if not match:
        return value[i:], None

    start, end = match.span()
    return value[i:start], end - 1

# Generic text file processing.

def get_list_from_file(filename):

    "Return a list of the words defined in 'filename'."

    if not filename:
        return None

    l = []

    f = codecs.open(filename, encoding="utf-8")
    try:
        for line in f.xreadlines():
            line = line.strip()
            if line:
                l.append(line)
    finally:
        f.close()

    return l

def get_map_from_file(filename):

    "Return a mapping from the words defined in 'filename'."

    if not filename:
        return None

    d = {}

    f = codecs.open(filename, encoding="utf-8")
    try:
        for line in f.xreadlines():
            line = line.strip()
            if line:
                key, value = line.split(None, 1)
                d[key] = value
    finally:
        f.close()

    return d

# Command option handling.

def get_option(name, default=None, missing=None, conversion=None):

    """
    Return the value following the command option 'name' or 'default' if the
    option was found without a following value. Return 'missing' if the option
    was missing.

    If 'conversion' is indicated, attempt to call it with any found value as
    argument, returning the result. Without a valid value, 'missing' is
    returned.
    """

    try:
        i = sys.argv.index(name)
        del sys.argv[i]
        value = sys.argv[i]
        del sys.argv[i]

        # Convert if requested.

        if conversion:
            return conversion(value)
        else:
            return value

    # Without an explicit value.

    except IndexError:
        return default

    # Without the option or with an invalid value.

    except ValueError:
        return missing

# vim: tabstop=4 expandtab shiftwidth=4
