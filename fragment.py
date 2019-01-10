#!/usr/bin/env python
# -*- coding: utf-8

"""
Collect words into the identified fragments, reducing the words to only those
of importance. Define fragment similarity by identifying common terms,
potentially weighting some terms as being more significant than others.
Produce a graph describing the fragments and their relationships.

Using a visualisation tool to show the graph has limited benefit. The
relationships between pairs of fragments are most important in this application.
However, a layout algorithm will attempt to reconcile the demands made by each
relationship simultaneously. Consequently, two fragments that have a high
similarity may be pulled apart by the relationships such fragments have with
others.
"""

from inputs import get_categorised_fragments, populate_fragments

from objects import Category, Fragment, Term, \
                    commit_text, compare_fragments, \
                    get_category_terms, get_fragment_terms, \
                    word_document_frequencies, word_frequencies

from collections import defaultdict
from math import log
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem.snowball import SnowballStemmer
from os import mkdir
from os.path import isdir, join
from xml.dom.minidom import parse
import codecs
import sys
import unicodedata

# Word processing.

def lower(words):

    "Convert 'words' to lower case unless a multi-word term."

    # NOTE: Could usefully employ part-of-speech tags to avoid lower-casing
    # NOTE: proper nouns.

    l = []
    for word in words:
        if not " " in word:
            l.append(word.lower())
        else:
            l.append(word)
    return l

def _normalise_accents(s):

    "Convert in 's' all grave accents to acute accents."

    return unicodedata.normalize("NFC",
        unicodedata.normalize("NFD", s).replace(u"\u0300", u"\u0301"))

normalise_accents = lambda l: map(_normalise_accents, map(unicode, l))

punctuation = ",;.:?!"

def remove_punctuation(s):
    for c in punctuation:
        s = s.replace(c, "")
    return s

def only_words(words):

    "Filter out non-words, principally anything that is punctuation."

    l = []
    for word in words:
        word = remove_punctuation(word).strip()
        if word:
            l.append(word)
    return l

# Provisional stop words.
# NOTE: Should be in a file, but really should be provided by NLTK or similar.
# NOTE: Moreover, these stop words would be better filtered out using
# NOTE: part-of-speech tagging.

#stop_words = map(lambda s: unicode(s, "utf-8"),
#["a", "al", "como", "con", "da", "de", "el", "en", "era", "es", "esa", "eso",
#"la", "las", "les", "lo", "los", "más", "me", "mi", "mí", "muy", "no", "o",
#"por", "porque", "que", "se", "si", "un", "una", "uno", "y", "yo"])

stop_words = [u"ahí", u"da", u"entonces", u"si", u"u"]

def no_stop_words(words):
    l = []
    # NLTK stop words. These may not be entirely appropriate or sufficient for
    # this application.
    stop = stop_words + stopwords.words("spanish")
    for word in words:
        if not word.lower() in stop:
            l.append(word)
    return l

# Stemming using NLTK.

def stem_words(words):
    stemmer = SnowballStemmer("spanish")
    l = []
    for word in words:
        l.append(stemmer.stem(word))
    return l

# Mapping via WordNet.

def map_to_synonyms(words):

    "Map 'words' to synonyms for normalisation."

    l = []
    for word in words:
        s = set()
        for synset in wn.synsets(word, lang="spa"):
            for synonym in synset.lemma_names(lang="spa"):
                s.add(synonym)
        l.append(Term(word, s))

    return l

# Simple grouping of words into terms.

def group_words(words):

    "Group 'words' into terms."

    words = group_names(words)
    words = group_quantities(words)
    return words

def group_names(words):

    "Group 'words' into terms for names."

    # NOTE: Use word features to support this correctly.
    filler_words = ["de", "la", "las", "lo", "los"]

    l = []
    term = []
    filler = []

    for word in words:

        # Add upper-cased words, incorporating any filler words.

        if word.isupper() or word.istitle():
            if filler:
                term += filler
                filler = []
            term.append(word)

        # Queue up filler words.

        elif term and word in filler_words:
            filler.append(word)

        # Handle other words.

        else:
            if term:
                l.append(" ".join(term))
                term = []
            if filler:
                l += filler
                filler = []
            l.append(word)

    if term:
        l.append(" ".join(term))
    if filler:
        l += filler
    return l

def group_quantities(words):

    "Group 'words' into terms for quantities."

    units = [u"años", u"días"]
    l = []
    term = []

    for word in words:
        if word.isdigit():
            if term:
                l.append(" ".join(term))
            term = [word]
        elif word in units:
            term.append(word)
            l.append(" ".join(term))
            term = []
        else:
            if term:
                l.append(" ".join(term))
                term = []
            l.append(word)

    if term:
        l.append(" ".join(term))
    return l

# Fragment processing.

def discard_empty_fragments(fragments):

    "Return a list of non-empty instances from 'fragments'."

    l = []
    for fragment in fragments:
        if fragment:
            l.append(fragment)
    return l

def get_all_words(fragments):

    "Return a sorted list of unique words."

    s = set()
    for fragment in fragments:
        s.update(fragment.words)
    l = list(s)
    l.sort()
    return l

def process_fragments(fragments, processes):

    """
    Process 'fragments' using the given 'processes', redefining the words (or
    terms) in the fragments.
    """

    for fragment in fragments:
        for process in processes:
            fragment.words = process(fragment.words)

# Term catalogues.

def get_common_terms(entity_terms):

    "Return a distribution mapping terms to common entities."

    d = defaultdict(set)
    for entity, terms in entity_terms.items():
        for term in terms:
            d[term].add(entity)
    return d

def inverse_document_frequencies(frequencies, numdocs):

    "Return the inverse document frequencies for 'frequencies' given 'numdocs'."

    d = {}
    for word, freq in frequencies.items():
        d[word] = log(float(numdocs) / (1 + freq), 10)
    return d

# Comparison functions.

def cmp_value_lengths(a, b):
    acat = len(a[1])
    bcat = len(b[1])
    return cmp(acat, bcat)

def cmp_values(a, b):
    return cmp(a[1], b[1])

# Output conversion.

def show_all_words(words, filename):
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
            terms = list(set(terms))
            terms.sort()
            print >>out, category
            for term in terms:
                print >>out, term
            print >>out
    finally:
        out.close()

def show_common_terms(common_terms, filename):

    """
    Show 'common_terms' in 'filename', this illustrating each term together with
    the entities (categories or fragments) in which it appears.
    """

    # Sort the terms and entities by increasing number of entities.

    l = common_terms.items()
    l.sort(cmp=cmp_value_lengths)

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for term, entities in l:
            print >>out, term, ",".join(map(lambda e: e.label(), entities))
    finally:
        out.close()

def show_connections(connections, filename):

    "Write a report of 'connections' to 'filename'."

    connections.sort(key=lambda x: x.measure())
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for connection in connections:
            for term, weight in connection.similarity:
                print >>out, term, weight,
            print >>out
            for fragment in connection.fragments:
                print >>out, fragment.text
            print >>out
    finally:
        out.close()

def show_fragments(fragments, filename):

    "Write the textual representation of 'fragments' to 'filename'."

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for fragment in fragments:
            print >>out, fragment # "\t".join(map(to_text, fragment.as_tuple()))
    finally:
        out.close()

def show_frequencies(frequencies, filename):

    "Write the mapping of term 'frequencies' to 'filename'."

    l = frequencies.items()
    l.sort(cmp=cmp_values)
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for word, occurrences in l:
            print >>out, word, occurrences
    finally:
        out.close()

def get_related_fragments(connections):

    """
    Using 'connections', show for each fragment the related fragments via the
    connections, writing the results to 'filename'.
    """

    # Visit all connections and collect for each fragment all the related
    # fragments together with the similarity details between the principal
    # fragment and each related fragment.

    d = defaultdict(list)
    for connection in connections:

        # The computed measure is used to rank the related fragments. General
        # similarity details are also included in the data for eventual output.

        measure = connection.measure()
        similarity = connection.similarity

        # Obtain related fragments for this connection. There should only be
        # one, but the connection supports relationships between more than two
        # fragments in general.

        for fragment, relations in connection.relations():
            for relation in relations:
                d[fragment].append((measure, relation, similarity))

    # NOTE: Sort fragments in descending order of similarity.

    return d.items()
    #l.sort(key=lambda i: i[1][0], reverse=True)
    #return l

def show_related_fragments(related, filename, shown_relations=5):

    """
    Show the 'related' fragments: for each fragment, show the related fragments
    via the connections, writing the results to 'filename'.
    """

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        for fragment, relations in related:

            # Show the related fragments in descending order of similarity.

            relations.sort(reverse=True)

            # Show the principal fragment details.

            print >>out, "  Id:", fragment.source, fragment.start, fragment.end
            print >>out, "Text:", fragment.text
            print >>out

            # For each related fragment, show details including the similarity
            # information.

            for measure, relation, similarity in relations[:shown_relations]:

                print >>out, "  Id:", relation.source, relation.start, relation.end
                print >>out, " Sim: %.2f" % measure,
                for term, score in similarity:
                    print >>out, "%s (%.2f)" % (term, score),
                print >>out
                print >>out, "Text:", relation.text
                print >>out

            if len(relations) > shown_relations:
                print >>out, "%d related fragments not shown." % (len(relations) - shown_relations)

            print >>out, "----"
            print >>out
    finally:
        out.close()

def to_text(i):
    if isinstance(i, (list, tuple)):
        return " ".join(map(to_text, i))
    else:
        return unicode(i).encode("utf-8")

graph_template = """\
graph fragments {
    node [shape=ellipse];
    %s
    %s
}
"""

node_template = """\
    %s [label="%s"];
"""

edge_template = """\
    %s -- %s [label="%s",len=%s];
"""

def write_graph(fragments, connections, filename):
    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        nodes = []
        for fragment in fragments:
            nodes.append(node_template % (id(fragment), fragment.label()))

        edges = []
        for connection in connections:
            edges.append(edge_template % (id(connection[0]), id(connection[1]), connection.label(), connection.label()))

        print >>out, graph_template % ("".join(nodes), "".join(edges))
    finally:
        out.close()

def ensure_directory(name):
    if not isdir(name):
        mkdir(name)

# Define the forms of filenames providing data.

datatypes = ["Text", "Tiers"]

def get_input_details(filename):
    for datatype in datatypes:
        if datatype in filename:
            return (datatype, filename.rsplit("_", 1)[0])
    return None

def get_input_filenames(args):
    d = defaultdict(set)
    for arg in args:
        details = get_input_details(arg)
        if details:
            datatype, basename = details
            d[basename].add((datatype, arg))
    l = []
    for basename, filenames in d.items():
        if len(filenames) == len(datatypes):
            lf = list(filenames)
            lf.sort()
            lf.insert(0, basename)
            l.append(lf)
    return l

helptext = """\
Need an output directory name plus a collection of text and tiers filenames for
reading. The output directory will be populated with files containing the
following:

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
 * illustration graphs
"""

# Main program.

if __name__ == "__main__":

    # Obtain filenames.

    try:
        outdir = sys.argv[1]
        filenames = sys.argv[2:]
    except (IndexError, ValueError):
        print >>sys.stderr, helptext
        sys.exit(1)

    # Derive filenames for output files.

    ensure_directory(outdir)

    fragmentsfn = join(outdir, "fragments.txt")
    connectionsfn = join(outdir, "connections.txt")
    wordsfn = join(outdir, "words.txt")
    termsfn = join(outdir, "terms.txt")
    ctermsfn = join(outdir, "term_categories.txt")
    ftermsfn = join(outdir, "term_fragments.txt")
    termfreqfn = join(outdir, "term_frequencies.txt")
    termdocfreqfn = join(outdir, "term_doc_frequencies.txt")
    terminvdocfreqfn = join(outdir, "term_inv_doc_frequencies.txt")
    relationsfn = join(outdir, "relations.txt")
    dotfn = join(outdir, "graph.dot")

    # For each fragment defined by the tiers, collect corresponding words, producing
    # fragment objects.

    fragments = []

    for source, (_datatype, textfn), (_datatype, tiersfn) in get_input_filenames(filenames):
        print tiersfn, textfn
        textdoc = parse(textfn)
        tiersdoc = parse(tiersfn)

        current_fragments = get_categorised_fragments(tiersdoc, source)
        populate_fragments(current_fragments, textdoc, source)

        fragments += current_fragments

    # Discard empty fragments.

    fragments = discard_empty_fragments(fragments)

    # NOTE: Should find a way of preserving capitalisation for proper nouns and not
    # NOTE: discarding articles/prepositions that feature in informative terms.
    # NOTE: Maybe chains of capitalised words that also include "padding" can be
    # NOTE: consolidated into single terms.

    commit_text(fragments)

    # Output words.

    all_words = get_all_words(fragments)
    show_all_words(all_words, wordsfn)

    # Perform some processes on the words:
    # Filtering of stop words.
    # Selection of dictionary words.
    # Part-of-speech tagging to select certain types of words (nouns and verbs).
    # Normalisation involving stemming, synonyms and semantic equivalences.

    processes = [group_words, only_words, map_to_synonyms, normalise_accents, lower, no_stop_words] #, stem_words]

    # Obtain only words, not punctuation.

    process_fragments(fragments, processes)

    # Emit the fragments for inspection.

    show_fragments(fragments, fragmentsfn)

    # Get terms used by each category for inspection.

    category_terms = get_category_terms(fragments)
    show_category_terms(category_terms, termsfn)

    # Get common terms (common between categories).

    common_category_terms = get_common_terms(category_terms)
    show_common_terms(common_category_terms, ctermsfn)

    # Get common terms (common between fragments).

    fragment_terms = get_fragment_terms(fragments)

    common_fragment_terms = get_common_terms(fragment_terms)
    show_common_terms(common_fragment_terms, ftermsfn)

    # Get term/word frequencies.

    frequencies = word_frequencies(fragments)
    show_frequencies(frequencies, termfreqfn)

    doc_frequencies = word_document_frequencies(fragments)
    show_frequencies(doc_frequencies, termdocfreqfn)

    inv_doc_frequencies = inverse_document_frequencies(doc_frequencies, len(fragments))
    show_frequencies(inv_doc_frequencies, terminvdocfreqfn)

    # Determine fragment similarity by taking the processed words and comparing
    # fragments.

    connections = compare_fragments(fragments, inv_doc_frequencies)

    # Emit the connections for inspection.

    show_connections(connections, connectionsfn)

    related = get_related_fragments(connections)
    show_related_fragments(related, relationsfn)

    # Produce a graph where each fragment is a node and the similarity (where
    # non-zero) is an edge linking the fragments.

    write_graph(fragments, connections, dotfn)

# vim: tabstop=4 expandtab shiftwidth=4
