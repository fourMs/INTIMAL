#!/usr/bin/env python
# -*- coding: utf-8

"""
Output production.
"""

from objects import ConnectedFragment, Term
from utils import cmp_value_lengths_and_keys, cmp_values_and_keys

from os import listdir, mkdir, remove
from os.path import exists, isdir, join
import codecs

# Output file handling.

class Output:

    "A container for output files."

    def __init__(self, outdir):
        self.outdir = outdir
        ensure_directory(self.outdir)

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
            print >>out, word
    finally:
        out.close()

def show_category_terms(category_terms, filename):

    """
    Show the 'category_terms' mapping in 'filename', with each correspondence in
    the mapping being formatted as the category followed by each distinct term
    associated with the category.
    """

    l = category_terms.items()
    l.sort()
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for category, terms in l:

            # Sort a list of distinct terms.

            terms = list(set(terms))
            terms.sort()

            # Show a category heading.

            s = unicode(category)
            print >>out, s
            print >>out, "-" * len(s)

            # Show the terms.

            for term in terms:
                print >>out, unicode(term)

            print >>out
    finally:
        out.close()

def show_common_terms(common_terms, filename):

    """
    Show 'common_terms' in 'filename', this illustrating each term together with
    the entities (categories or fragments) in which it appears.
    """

    # Sort the terms and entities by increasing number of entities and by terms.

    l = common_terms.items()
    l.sort(cmp=cmp_value_lengths_and_keys)

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for term, entities in l:

            # Sort a list of distinct entities.

            entities = list(set(entities))
            entities.sort()

            print >>out, unicode(term), ",".join(map(lambda e: e and unicode(e) or "null", entities))
    finally:
        out.close()

def show_connections(connections, filename, brief=False):

    "Write a report of 'connections' to 'filename'."

    j = rjust

    connections.sort(key=lambda x: x.measure())
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for connection in connections:
            show_similarity(connection, out)

            # Show the connected fragments.

            for fragment in connection.fragments:

                # For brief output, just show the source details.

                if brief:
                    print >>out, j("Source:"), unicode(fragment.source)
                else:
                    show_fragment(fragment, out)

            print >>out
    finally:
        out.close()

def show_fragments(fragments, filename):

    "Write a report of 'fragments' to 'filename'."

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for fragment in fragments:
            show_fragment(fragment, out, terms=True)
            print >>out
    finally:
        out.close()

def show_frequencies(frequencies, filename):

    "Write the mapping of term 'frequencies' to 'filename'."

    l = frequencies.items()
    l.sort(cmp=cmp_values_and_keys)
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for term, occurrences in l:
            print >>out, unicode(term), occurrences
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

        related_items = related.items()
        related_items.sort()

        for fragment, connections in related_items:

            # Show the principal details of each fragment.

            show_fragment(fragment, out)
            print >>out

            # For each related fragment, show details including the similarity
            # information.

            to_show = shown_relations

            for relation, connection in ConnectedFragment(fragment, connections):
                if not to_show:
                    break

                show_similarity(connection, out)
                show_fragment(relation, out)
                print >>out

                to_show -= 1

            # In case the number of related fragments was not limited, limit it
            # to the parameterised number.

            if len(connections) > shown_relations:
                print >>out, "%d related fragments not shown." % (len(connections) - shown_relations)

            # Make a separator after the fragments.

            print >>out, "----"
            print >>out

    finally:
        out.close()

def show_fragment(fragment, out, terms=False):

    "Show the principal details of 'fragment' using 'out'."

    j = rjust

    print >>out, j("Source:"), unicode(fragment.source)
    print >>out, j("Category:"), unicode(fragment.category)
    print >>out, j("Text:"), fragment.text

    if terms:
        print >>out, j("Terms:"), u" ".join(map(term_summary, fragment.words))

def show_similarity(connection, out):

    "Show similarity information for 'connection' using 'out'."

    j = rjust

    print >>out, j("Sim:"), "%.2f" % connection.measure(),

    similarities = connection.similarity.items()
    similarities.sort()

    for term, score in similarities:
        print >>out, "%s (%.2f)" % (quoted(term), score),

    print >>out

# Output utilities.

def rjust(s, width=9):

    "Right-justify 's' to 'width'."

    return s.rjust(width)

def term_summary(term):

    "Produce a readable summary of 'term'."

    if isinstance(term, Term):
        tag = term.tag and ":%s" % term.tag or ""
        norm = term.normalised and ":%s" % quoted(term.normalised) or ""
        return u"%s%s%s" % (quoted(term.word), tag, norm)
    else:
        return quoted(term)

def quoted(term):

    "Quote the 'term' using quotation marks where spaces appear in the term."

    s = unicode(term)
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

            # Write connection information for the dataset in a new subdirectory.

            dataset_out = fragment_out.subdir(label)

            # Remove any existing files in the subdirectory.

            for filename in dataset_out.filenames():
                remove(filename)

            for i, (relation, connection) in enumerate(ConnectedFragment(fragment, connections)):
                writefile(dataset_out.filename(str(i)), str(relation.source))

# vim: tabstop=4 expandtab shiftwidth=4
