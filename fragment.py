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

#import networkx
#from networkx.drawing.nx_pydot import write_dot

from collections import defaultdict
from math import log
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem.snowball import SnowballStemmer
from os import mkdir
from os.path import isdir, join
from xml.dom.minidom import parse
import bisect
import codecs
import itertools
import sys
import unicodedata

class Category:

	"A complete category description."

	def __init__(self, parent, category):
		self.parent = parent
		self.category = category

	def __cmp__(self, other):
		return cmp(self.as_tuple(), other.as_tuple())
		
	def __hash__(self):
		return hash(self.as_tuple())

	def __repr__(self):
		return "Category(%r, %r)" % self.as_tuple()
	
	def __str__(self):
		return "%s-%s" % self.as_tuple()

	def as_tuple(self):
		return (self.parent, self.category)

	# Graph methods.

	def label(self):
		return str(self)

class Connection:

	"A connection between two fragments."

	def __init__(self, similarity, fragments):

		"""
		Initialise a connection with the given 'similarity' and 'fragments'
		involved.
		"""

		self.similarity = similarity
		self.fragments = fragments

	def __cmp__(self, other):
		key = self.measure(), self.similarity
		other_key = other.measure(), other.similarity
		if key < other_key:
			return -1
		elif key > other_key:
			return 1
		else:
			return 0

	def __hash__(self):
		return hash(tuple(map(hash, self.fragments)))

	def __repr__(self):
		return "Connection(%r, %r)" % self.as_tuple()

	def as_tuple(self):
		return (self.similarity, self.fragments)

	def label(self):
		return self.measure()
	
	def measure(self):
		m = 0
		for term, measure in self.similarity:
			m += measure
		return m

	def relations(self):
		l = []
		for i, fragment in enumerate(self.fragments):
			l.append((fragment, self.fragments[:i] + self.fragments[i+1:]))
		return l

	# For NetworkX, support node access.

	def __getitem__(self, item):
		if item in (0, 1, -3, -2):
			return self.fragments[:2][item]
		elif item in (2, -1):
			return {"weight" : self.measure()}
		else:
			raise IndexError, item

	def __len__(self):
		# For NetworkX, pretend to be a tuple of the form
		# (node1, node2, data)
		return 3

class Fragment:

	"A fragment of text from a transcript."
	
	def __init__(self, source, start, end, parent, category, words=None, text=None):
	
		"""
		Initialise a fragment from 'source' with the given 'start' and 'end'
		timings, the nominated 'parent' and leaf 'category', and a collection of
		corresponding 'words'. Any original 'text' words may be set or instead
		committed later using the 'commit_text' method.
		"""

		self.source = source
		self.start = start
		self.end = end
		self.parent = parent
		self.category = category
		self.words = words or []
		self.text = text

	def __cmp__(self, other):

		"Compare this fragment to 'other'."
		
		if self.start < other.start:
			return -1
		elif self.start > other.start:
			return 1
		else:
			return 0

	def __hash__(self):
		return hash((self.source, self.start, self.end, self.parent, self.category))

	def __nonzero__(self):
		return bool(self.words)

	def __repr__(self):
		return "Fragment(%r, %r, %r, %r, %r, %r, %r)" % self.as_tuple()

	def as_tuple(self):
		return (self.source, self.start, self.end, self.parent, self.category, self.words, self.text)

	def commit_text(self):
		self.text = " ".join(self.words)

	def similarity(self, other, idf=None):
		return similarity(self.word_frequencies(), other.word_frequencies(), idf)

	def word_frequencies(self):
		d = defaultdict(lambda: 0)
		for word in self.words:
			d[word] += 1
		return d

	# Graph methods.

	def label(self):
		return "%s:%s-%s" % (self.source, self.start, self.end)

def textContent(n):
	l = []
	for t in n.childNodes:
		l.append(t.nodeValue)
	return "".join(l)

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

normalise_accents = lambda l: map(_normalise_accents, l)

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

stop_words = [u"da", u"entonces", u"si", u"u"]

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
				s.add(word)
		l.append(s)

	return words

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

# Fragment retrieval.

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
				fragments.append(Fragment(source, start, end, parent, textContent(category)))
				break

	fragments.sort()
	return fragments

def populate_fragments(fragments, textdoc, source):

	"Populate the 'fragments' using information from 'textdoc' for 'source'."

	for span in textdoc.getElementsByTagName("span"):
		start = float(span.getAttribute("start"))
		end = float(span.getAttribute("end"))
		
		# The word is textual content within a subnode.
		
		for word in span.getElementsByTagName("v"):
			temp = Fragment(source, start, end, None, None, [textContent(word)])
			break
		else:
			continue

		# Find the appropriate fragment.

		i = bisect.bisect_right(fragments, temp)
		
		if i > 0:
			i -= 1
			
		f = fragments[i]
		
		if f.end > temp.start >= f.start:
			f.words += temp.words

def commit_text(fragments):

	"Preserve the original text in the 'fragments'."

	for fragment in fragments:
		fragment.commit_text()

# Fragment processing.

def compare_fragments(fragments, idf=None):

	"""
	Compare 'fragments' with each other, returning a list of connections
	sorted by the similarity measure. If 'idf' is given, use this inverse
	document frequency distribution to scale term weights.
	"""

	connections = []

	for f1, f2 in itertools.combinations(fragments, 2):
		similarity = f1.similarity(f2, idf)
		if similarity:
			connections.append(Connection(similarity, (f1, f2)))

	connections.sort(key=lambda c: c.measure())
	return connections

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

def get_category_terms(fragments):

	"Return a dictionary mapping categories to terms."

	d = defaultdict(list)
	for fragment in fragments:
		for word in fragment.words:
			d[Category(fragment.parent, fragment.category)].append(word)
	return d

def get_common_terms(entity_terms):

	"Return a distribution mapping terms to common entities."

	d = defaultdict(set)
	for entity, terms in entity_terms.items():
		for term in terms:
			d[term].add(entity)
	return d

def get_fragment_terms(fragments):

	"Return a dictionary mapping fragments to terms."

	d = {}
	for fragment in fragments:
		d[fragment] = fragment.words
	return d

# Fragment similarity calculations.

def similarity(f1, f2, idf=None):

	"""
	Return similarity details for words/terms found in both 'f1' and 'f2',
	these being frequency distributions for two fragments. If 'idf' is given,
	use this inverse document frequency distribution to scale term weights.
	"""

	# Total frequencies can be used to scale each term in order to measure its
	# prevalence in a fragment.

	total1 = sum_values(f1)
	total2 = sum_values(f2)
	
	d = {}
	for term, freq in f1.items():
		if f2.has_key(term):
			idf_for_term = idf and idf[term] or 1
			#d[term] = (float(freq) / total1 + float(f2[term]) / total2) * idf_for_term
			d[term] = scaled_frequency_idf(freq, f2[term], total1, total2, idf_for_term)
	return d.items()

def absolute_frequency_idf(freq1, freq2, idf):
	return float(freq1 + freq2) / idf

def scaled_frequency_idf(freq1, freq2, total1, total2, idf):
	return float(freq1 + freq2) / (total1 + total2) * idf

def sum_values(d):
	t = 0
	for value in d.values():
		t += value
	return t

def word_document_frequencies(fragments):

	"Return document frequencies for words from the 'fragments'."

	d = defaultdict(lambda: 0)
	for fragment in fragments:
		for word in fragment.word_frequencies().keys():
			d[word] += 1
	return d

def word_frequencies(fragments):

	"Merge word frequencies from the given 'fragments'."

	d = defaultdict(lambda: 0)
	for fragment in fragments:
		for word, occurrences in fragment.word_frequencies().items():
			d[word] += occurrences
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

def show_related_fragments(connections, filename, shown_relations=5):

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

	# Show each fragment with related fragments in descending order of
	# similarity.

	l = d.items()
	l.sort()

	out = codecs.open(filename, "w", encoding="utf-8")
	try:
		for fragment, relations in l:

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

	processes = [group_words, only_words, normalise_accents, lower, no_stop_words] #, stem_words]

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

	show_related_fragments(connections, relationsfn)

	# Produce a graph where each fragment is a node and the similarity (where
	# non-zero) is an edge linking the fragments.

	#graph = networkx.Graph()
	#graph.add_nodes_from(fragments)
	#graph.add_edges_from(connections)
	#pos = networkx.nx_pydot.graphviz_layout(graph)
	#networkx.draw(graph, pos=pos)
	#write_dot(graph, "xxx.dot")

	write_graph(fragments, connections, dotfn)
