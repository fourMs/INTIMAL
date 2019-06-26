#!/usr/bin/env python3
# -*- coding: utf-8

"""
Output production.

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

from objects import Term
from utils import cmp_value_lengths_and_keys, cmp_values_and_keys

from os import listdir, mkdir, remove, rmdir
from os.path import exists, isdir, join
import codecs

# Output file handling.

class Output:

    "A container for output files."

    def __init__(self, outdir):
        self.outdir = outdir
        ensure_directory(self.outdir)

        # Data retained for potential output.

        self.data = {}

    # Data retention methods.

    def __contains__(self, key):
        return key in self.data

    def __delitem__(self, key):
        del self.data[key]

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def has_key(self, key):
        return key in self.data

    def keys(self):
        return self.data.keys()

    # Filesystem-related methods.

    def clean(self, recursive=False):
        for filename in self.filenames():
            if not isdir(filename):
                remove(filename)
            elif recursive:
                Output(filename).clean(True)
                rmdir(filename)

    def exists(self, name):
        return exists(self.filename(name))

    def filename(self, name):
        return join(self.outdir, name)

    def filenames(self):
        l = []
        for name in listdir(self.outdir):
            l.append(join(self.outdir, name))
        return l

    def subdir(self, name):
        return Output(self.filename(name))

def ensure_directory(name):

    "Make sure that directory 'name' exists."

    if not isdir(name):
        mkdir(name)

def writefile(filename, text):

    "Write to 'filename' the given 'text'."

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        out.write(text)
    finally:
        out.close()

# Output conversion.

def show_all_words(words, filename):

    "Show 'words' in 'filename'."

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for word in words:
            print(word, file=out)
    finally:
        out.close()

def show_category_terms(category_terms, filename):

    """
    Show the 'category_terms' mapping in 'filename', with each correspondence in
    the mapping being formatted as the category followed by each distinct term
    associated with the category.
    """

    l = list(category_terms.items())
    l.sort()
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for category, terms in l:

            # Sort a list of distinct terms.

            terms = list(set(terms))
            terms.sort()

            # Show a category heading.

            s = str(category)
            print(s, file=out)
            print("-" * len(s), file=out)

            # Show the terms.

            for term in terms:
                print(str(term), file=out)

            print(file=out)
    finally:
        out.close()

def show_common_terms(common_terms, filename, delimiter=" ", summary=False):

    """
    Show 'common_terms' in 'filename', this illustrating each term together with
    the entities (categories or fragments) in which it appears. If 'delimiter'
    is specified then it is used to separate the terms and entities. If
    'summary' is specified and has a true value, the number of entities will be
    shown, not the actual entities themselves.
    """

    # Sort the terms and entities by increasing number of entities and by terms.

    l = list(common_terms.items())
    l.sort(cmp=cmp_value_lengths_and_keys)

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for term, entities in l:
            if summary:
                print("%s%s%s" % (str(term), delimiter, len(entities)), file=out)
            else:
                # Sort a list of distinct entities.

                entities = list(set(entities))
                entities.sort()

                labels = map(lambda e: e and str(e) or "null", entities)
                print("%s%s%s" % (str(term), delimiter, ",".join(labels)), file=out)
    finally:
        out.close()

def show_connections(connections, filename, brief=False):

    "Write a report of 'connections' to 'filename'."

    j = rjust

    connections.sort(key=lambda x: x.measure())
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for connection in connections:

            # Only show similarity details for verbose output.

            if not brief:
                show_similarity(connection, out)
                print(file=out)

            # Show the connected fragments.

            for fragment in connection.fragments:

                # For brief output, just show the source details.

                if brief:
                    print(j("Source:"), str(fragment.source), file=out)
                else:
                    show_fragment(fragment, out)

            print(file=out)
    finally:
        out.close()

def show_fragments(fragments, filename):

    "Write a report of 'fragments' to 'filename'."

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for fragment in fragments:
            show_fragment(fragment, out, terms=True)
            print(file=out)
    finally:
        out.close()

def show_frequencies(frequencies, filename):

    "Write the mapping of term 'frequencies' to 'filename'."

    l = list(frequencies.items())
    l.sort(cmp=cmp_values_and_keys)
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for term, occurrences in l:
            print(str(term), occurrences, file=out)
    finally:
        out.close()

def show_fragment_accessibility(accessibility, filename):

    """
    Show the 'accessibility' mapping in summary form, indicating the number of
    fragments able to access each given fragment, writing the results to
    'filename'.
    """

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for fragment, related in accessibility.items():
            print(str(fragment.source), len(related), file=out)
    finally:
        out.close()

def show_related_fragments(related, filename, shown_relations=5):

    """
    Show the 'related' fragments: for each fragment, show the related fragments
    via the connections, writing the results to 'filename'.
    """

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        # Sort the fragments for output.

        related_items = list(related.items())
        related_items.sort()

        for fragment, connections in related_items:

            # Show the principal details of each fragment.

            show_fragment(fragment, out)
            print(file=out)

            # For each related fragment, show details including the similarity
            # information.

            to_show = shown_relations

            for connection in connections:
                if not to_show:
                    break

                relation = connection.relation(fragment)

                show_similarity(connection, out)
                print(file=out)
                show_fragment(relation, out)
                print(file=out)

                to_show -= 1

            # In case the number of related fragments was not limited, limit it
            # to the parameterised number.

            if len(connections) > shown_relations:
                print("%d related fragments not shown." % (len(connections) - shown_relations), file=out)

            # Make a separator after the fragments.

            print("----", file=out)
            print(file=out)

    finally:
        out.close()

def show_fragment(fragment, out, terms=False):

    "Show the principal details of 'fragment' using 'out'."

    j = rjust

    print(j("Source:"), str(fragment.source), file=out)
    print(j("Category:"), str(fragment.category), file=out)
    print(j("Text:"), fragment.text, file=out)

    if terms:
        print(j("Terms:"), " ".join(map(term_summary, fragment.words)), file=out)

def show_similarity(connection, out):

    "Show similarity information for 'connection' using 'out'."

    j = rjust

    print(j("Sim:"), "%.2f" % connection.measure(), end=" ", file=out)
    print(similarity_details(connection), file=out)

# Output utilities.

def rjust(s, width=9):

    "Right-justify 's' to 'width'."

    return s.rjust(width)

def similarity_details(connection):

    "Return a string containing the similarity details for 'connection'."

    similarities = list(connection.similarity.items())
    similarities.sort()

    l = []

    for term, score in similarities:
        l.append("%s (%.2f)" % (quoted(term), score))

    return " ".join(l)

def term_summary(term):

    "Produce a readable summary of 'term'."

    if isinstance(term, Term):
        tag = term.tag and ":%s" % term.tag or ""
        norm = term.normalised and ":%s" % quoted(term.normalised) or ""
        return "%s%s%s" % (quoted(term.word), tag, norm)
    else:
        return quoted(term)

def quoted(term):

    "Quote the 'term' using quotation marks where spaces appear in the term."

    s = str(term)
    if " " in s:
        return u'"%s"' % s
    else:
        return s

# Structured output.

def write_fragment_data(datasets, dirname):

    "Write fragment 'datasets' to 'dirname'."

    output = Output(dirname)

    for label, related in datasets:

        # Process each fragment in the dataset along with its relations.

        for fragment, connections in related.items():

            # Obtain a subdirectory for the fragment data.

            fragment_out = output.subdir(str(fragment.source))

            # Write files containing the fragment details to a file in the
            # subdirectory.

            if not fragment_out.exists("text"):
                writefile(fragment_out.filename("text"), fragment.text)
                writefile(fragment_out.filename("category"), str(fragment.category))

            # Write connection information for the dataset in a new subdirectory.

            dataset_out = fragment_out.subdir(label)
            dataset_out.clean(recursive=True)

            for i, connection in enumerate(connections):
                relation_out = dataset_out.subdir(str(i))
                relation = connection.relation(fragment)

                writefile(relation_out.filename("fragment"), str(relation.source))
                writefile(relation_out.filename("measure"), str(connection.measure()))
                writefile(relation_out.filename("similarity"), similarity_details(connection))

# vim: tabstop=4 expandtab shiftwidth=4
