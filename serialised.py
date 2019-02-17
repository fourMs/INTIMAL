#!/usr/bin/env python
# -*- coding: utf-8

"""
Serialised object processing.
"""

from objects import Category, Connection, Fragment, Source, Term

import codecs
import re

def get_serialised_connections(filename, fragments):

    """
    Return a list of connections serialised in 'filename', linked to the given
    'fragments'.
    """

    source_to_fragment = dict(map(lambda f: (f.source, f), fragments))

    l = []

    f = codecs.open(filename, encoding="utf-8")
    try:
        current = Connection(None, [])

        while True:

            # Read each line (xreadlines seems to return plain strings).

            line = f.readline()

            if not line:
                break

            # Remove trailing newlines and complete the current connection if a
            # blank line is encountered.

            line = line.rstrip("\n")

            if not line:
                if current:
                    l.append(current)
                    current = Connection(None, [])
                continue

            # Parse a record and modify the current connection.

            key, value = line.split(": ", 1)
            key = key.lstrip()

            if key == "Sim":
                current.similarity = get_serialised_similarity(value)
            elif key == "Source":
                source = get_serialised_source(value)

                # Find the referenced fragment.

                fragment = source_to_fragment.get(source)
                if fragment:
                    current.fragments.append(fragment)

        # Complete the current connection.

        if current:
            l.append(current)

    finally:
        f.close()

    return l

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

def get_serialised_similarity(value):

    "Return similarity details from the given serialised 'value'."

    # Remove the measure.

    measure, value = value.split(None, 1)

    # Acquire each term and weight.

    l = []
    i = 0

    while i < len(value):
        term, i = get_term_from_summary(value, i)

        if i is None:
            break

        # Parse the weight.

        start = value.find("(", i)
        end = value.find(")", i)

        if start != -1 and end != -1 and start < end:
            try:
                weight = float(value[start+1:end])
            except ValueError:
                break

            l.append((term, weight))
        else:
            break

        # Move on to the next term.

        i = end + 2

    return dict(l)

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

        # Move on to the next term.

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

# vim: tabstop=4 expandtab shiftwidth=4
