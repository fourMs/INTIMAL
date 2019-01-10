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
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
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

	def __init__(self, overlap, fragments):

		"""
		Initialise a connection with the given 'overlap' and 'fragments'
		involved.
		"""

		self.overlap = overlap
		self.fragments = fragments

	def __cmp__(self, other):
		key = self.measure(), self.overlap
		other_key = other.measure(), other.overlap
		if key < other_key:
			return -1
		elif key > other_key:
			return 1
		else:
			return 0

	def __getitem__(self, item):
		# For NetworkX, support node access.
		if item in (0, 1, -3, -2):
			return self.fragments[:2][item]
		elif item in (2, -1):
			return {"weight" : self.measure()}
		else:
			raise IndexError, item

	def __hash__(self):
		return hash(tuple(map(hash, self.fragments)))

	def __len__(self):
		# For NetworkX, pretend to be a tuple of the form
		# (node1, node2, data)
		return 3

	def __repr__(self):
		return "Connection(%r, %r)" % self.as_tuple()

	def as_tuple(self):
		return (self.overlap, self.fragments)

	def label(self):
		return self.measure()
	
	def measure(self):
		m = 0
		for term, measure in self.overlap:
			m += measure
		return m

class Fragment:

	"A fragment of text from a transcript."
	
	def __init__(self, start, end, parent, category, words=None, text=None):
	
		"""
		Initialise a fragment with the given 'start' and 'end' timings, the
		nominated 'parent' and leaf 'category', and a collection of
		corresponding 'words'. Any original 'text' words may be set or instead
		committed later using the 'commit_text' method.
		"""
		
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
		return hash((self.start, self.end, self.parent, self.category))
	
	def __repr__(self):
		return "Fragment(%r, %r, %r, %r, %r, %r)" % self.as_tuple()

	def as_tuple(self):
		return (self.start, self.end, self.parent, self.category, self.words, self.text)

	def commit_text(self):
		self.text = self.words

	def overlap(self, other):
		return intersection(self.words, other.words)

	# Graph methods.

	def label(self):
		return "%s-%s" % (self.start, self.end)

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

stop_words = [u"da", u"si", u"u"]

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

def get_categorised_fragments(tiersdoc):

	"Using the 'tiersdoc' return a sorted list of fragments."

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
				fragments.append(Fragment(start, end, parent, textContent(category)))
				break

	fragments.sort()
	return fragments

def populate_fragments(fragments, textdoc):

	"Populate the 'fragments' using information from 'textdoc'."

	for span in textdoc.getElementsByTagName("span"):
		start = float(span.getAttribute("start"))
		end = float(span.getAttribute("end"))
		
		# The word is textual content within a subnode.
		
		for word in span.getElementsByTagName("v"):
			temp = Fragment(start, end, None, None, [textContent(word)])
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

def compare_fragments(fragments):

	"""
	Compare 'fragments' with each other, returning a list of connections
	sorted by the similarity measure.
	"""

	connections = []

	for f1, f2 in itertools.combinations(fragments, 2):
		overlap = f1.overlap(f2)
		if overlap:
			connections.append(Connection(overlap, (f1, f2)))

	connections.sort()
	return connections

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

# Term frequency calculations.

def frequencies(l):
	d = {}
	for i in set(l):
		d[i] = l.count(i)
	return d

def intersection(l1, l2):

	# NOTE: This should consider word importance.

	f = frequencies(l1 + l2)
	l = []
	for i in set(l1).intersection(l2):
		l.append((i, f[i]))
	return l

# Output conversion.

def show_category_terms(category_terms, filename):
	out = codecs.open(filename, "w", encoding="utf-8")
	l = category_terms.items()
	l.sort()
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

def cmp_term_entities(a, b):
	acat = len(a[1])
	bcat = len(b[1])
	return cmp(acat, bcat)

def show_common_terms(common_terms, filename):
	out = codecs.open(filename, "w", encoding="utf-8")
	l = common_terms.items()
	l.sort(cmp=cmp_term_entities)
	try:
		for term, entities in l:
			print >>out, term, ",".join(map(lambda e: e.label(), entities))
	finally:
		out.close()

def show_connections(connections, filename):
	out = codecs.open(filename, "w", encoding="utf-8")
	try:
		for connection in connections:
			print >>out, connection
	finally:
		out.close()

def show_fragments(fragments, filename):
	out = codecs.open(filename, "w", encoding="utf-8")
	try:
		for fragment in fragments:
			print >>out, fragment # "\t".join(map(to_text, fragment.as_tuple()))
	finally:
		out.close()

def to_text(i):
	if isinstance(i, (list, tuple)):
		return " ".join(map(to_text, i))
	else:
		return unicode(i).encode("utf-8")

# Main program.

if __name__ == "__main__":

	# Obtain filenames.

	try:
		textfn, tiersfn, fragmentsfn, connectionsfn, termsfn, ctermsfn, ftermsfn = sys.argv[1:8]
	except ValueError:
		print >>sys.stderr, """\
	Need a text file and a tiers file for reading, plus filenames for the
	fragments, connections, category terms, common category terms and common
	fragment terms.
	"""
		sys.exit(1)

	# For each fragment defined by the tiers, collect corresponding words, producing
	# fragment objects.

	textdoc = parse(textfn)
	tiersdoc = parse(tiersfn)

	fragments = get_categorised_fragments(tiersdoc)
	populate_fragments(fragments, textdoc)

	# NOTE: Should find a way of preserving capitalisation for proper nouns and not
	# NOTE: discarding articles/prepositions that feature in informative terms.
	# NOTE: Maybe chains of capitalised words that also include "padding" can be
	# NOTE: consolidated into single terms.

	process_fragments(fragments, [group_words, only_words])
	commit_text(fragments)

	# Emit the fragments for inspection.

	show_fragments(fragments, fragmentsfn)

	# Perform some processes on the words:
	# Filtering of stop words.
	# Selection of dictionary words.
	# Part-of-speech tagging to select certain types of words (nouns and verbs).
	# Normalisation involving stemming, synonyms and semantic equivalences.

	processes = [normalise_accents, lower, no_stop_words] #, stem_words]

	# Obtain only words, not punctuation.

	process_fragments(fragments, processes)

	# Get terms used by each category for inspection.

	category_terms = get_category_terms(fragments)
	show_category_terms(category_terms, termsfn)

	common_category_terms = get_common_terms(category_terms)
	show_common_terms(common_category_terms, ctermsfn)

	fragment_terms = get_fragment_terms(fragments)

	common_fragment_terms = get_common_terms(fragment_terms)
	show_common_terms(common_fragment_terms, ftermsfn)

	# Determine fragment similarity by taking the processed words and comparing
	# fragments.

	connections = compare_fragments(fragments)

	# Emit the connections for inspection.

	show_connections(connections, connectionsfn)

	# Produce a graph where each fragment is a node and the similarity (where
	# non-zero) is an edge linking the fragments.

	#graph = networkx.Graph()
	#graph.add_nodes_from(fragments)
	#graph.add_edges_from(connections)
	#pos = networkx.nx_pydot.graphviz_layout(graph)
	#networkx.draw(graph, pos=pos)
	#write_dot(graph, "xxx.dot")

	template = """\
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

	nodes = []
	for fragment in fragments:
		nodes.append(node_template % (id(fragment), fragment.label()))

	edges = []
	for connection in connections:
		edges.append(edge_template % (id(connection[0]), id(connection[1]), connection.label(), connection.label()))

	print template % ("".join(nodes), "".join(edges))
