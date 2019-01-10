#!/usr/bin/env python
# -*- coding: utf-8

"""
Fragment retrieval.
"""

from objects import Fragment
import bisect

# XML node processing.

def textContent(n):
	l = []
	for t in n.childNodes:
		l.append(t.nodeValue)
	return "".join(l)

# XML document processing.

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
