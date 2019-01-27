#!/usr/bin/env python
# -*- coding: utf-8

"""
Output production.
"""

from objects import Term
from utils import cmp_value_lengths_and_keys, cmp_values

from os import mkdir
from os.path import isdir, join
import codecs

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

def show_connections(connections, filename):

    "Write a report of 'connections' to 'filename'."

    connections.sort(key=lambda x: x.measure())
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for connection in connections:

            # Show terms and weights.

            similarities = connection.similarity.items()
            similarities.sort()

            for term, weight in similarities:
                print >>out, unicode(term), weight,

            print >>out

            # Show the connected fragments.

            for fragment in connection.fragments:
                print >>out, fragment.text

            print >>out
    finally:
        out.close()

def show_fragments(fragments, filename):

    "Write a report of 'fragments' to 'filename'."

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for fragment in fragments:
            print >>out, "Source:", unicode(fragment.source)
            print >>out, "Category:", unicode(fragment.category)
            print >>out, "Text:", fragment.text
            print >>out, "Terms:", u" ".join(map(term_summary, fragment.words))
            print >>out
    finally:
        out.close()

def show_frequencies(frequencies, filename):

    "Write the mapping of term 'frequencies' to 'filename'."

    l = frequencies.items()
    l.sort(cmp=cmp_values)
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
        for fragment, connections in related.items():

            # Show the related fragments in descending order of similarity.

            connections.sort(key=lambda x: x.measure(), reverse=True)

            # Show the principal fragment details.

            print >>out, "  Id:", fragment.source, fragment.source.start, fragment.source.end
            print >>out, "Text:", fragment.text
            print >>out

            # For each related fragment, show details including the similarity
            # information.

            to_show = shown_relations

            for connection in connections:
                if not to_show:
                    break

                # Obtain the related fragments.

                for relation in connection.relations(fragment):
                    if not to_show:
                        break

                    print >>out, "  Id:", relation.source, relation.source.start, relation.source.end

                    print >>out, " Sim: %.2f" % connection.measure(),

                    similarities = connection.similarity.items()
                    similarities.sort()

                    for term, score in similarities:
                        print >>out, "%s (%.2f)" % (unicode(term), score),

                    print >>out
                    print >>out, "Text:", relation.text
                    print >>out

                    to_show -= 1

            if len(connections) > shown_relations:
                print >>out, "%d related fragments not shown." % (len(connections) - shown_relations)

            print >>out, "----"
            print >>out
    finally:
        out.close()

def term_summary(term):

    "Produce a readable summary of 'term'."

    if isinstance(term, Term):
        return u"%s:%s" % (quoted(term), term.tag)
    else:
        return quoted(term)

def quoted(term):
    s = unicode(term)
    if " " in s:
        return u'"%s"' % s
    else:
        return s

# Output file handling.

class Output:

    "A container for output files."

    def __init__(self, outdir):
        self.outdir = outdir
        ensure_directory(self.outdir)

    def filename(self, name):
        return join(self.outdir, name)

def ensure_directory(name):
    if not isdir(name):
        mkdir(name)

# vim: tabstop=4 expandtab shiftwidth=4
