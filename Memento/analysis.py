#!/usr/bin/env python3
# -*- coding: utf-8

"""
Text/linguistic analysis.

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

----

Currently, this uses the spaCy toolkit:

https://spacy.io/

Another potentially-useful toolkit is Polyglot:

https://pypi.org/project/polyglot/
"""

from objects import Term
import spacy

nlp = None

def ensure_nlp(lang="es"):

    "Ensure that the language model for 'lang' is loaded."

    global nlp
    if not nlp:
        nlp = spacy.load(lang)

def get_tokens(s, lang="es"):

    "Return tokens for 's'."

    ensure_nlp(lang)
    return nlp(s)

def process_tokens(s, ops, lang="es"):

    "Process the tokens found by tokenising 's' with the given 'ops'."

    l = []
    for token in get_tokens(s, lang):
        t = token
        for op in ops:
            t = op(t)
            if not t:
                break
        else:
            l.append(t)
    return l

# Processing functions.

def lower_word(t):

    "Apply lower casing to the token in 't' if not a proper noun."

    token, result = t

    # Sometimes, articles appear in proper nouns.

    if token.pos_ not in ("DET", "PROPN",):
        return (token, result.lower())
    else:
        return t

def stem_word(t):

    "Stem the token in 't' if it is a verb or adjective."

    token, result = t

    if token.pos_ in ("ADJ", "NOUN", "VERB"):
        return (token, token.lemma_)
    else:
        return t

# Internal functions for setting up and finalising results.

def init_result(token):

    """
    Return a tuple containing 'token' and the initial result involving 'token'.
    """

    return (token, token.text)

def complete_result(t):

    "Return the eventual result from 't', this being (token, result)."

    token, result = t
    return Term(token.text, token.pos_, result)

# Fragment processing.

def process_fragment_tokens(fragments, ops):

    "Process the 'fragments' using the given 'ops'."

    for fragment in fragments:
        fragment.words = process_tokens(fragment.get_text(), [init_result] + ops + [complete_result])

# vim: tabstop=4 expandtab shiftwidth=4
