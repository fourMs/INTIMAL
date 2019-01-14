#!/usr/bin/env python
# -*- coding: utf-8

"""
Text/linguistic analysis.

Currently, this uses the spaCy toolkit:

https://spacy.io/

Another potentially-useful toolkit is Polyglot:

https://pypi.org/project/polyglot/
"""

from nltk.corpus import wordnet as wn
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

    if token.pos_ not in ("PROPN",):
        return (token, result.lower())
    else:
        return t

def stem_word(t):

    "Stem the token in 't' if it is a verb."

    token, result = t

    if token.pos_ == "VERB":
        return (token, token.lemma_)
    else:
        return t

def compare_pos(nltkpos, spacypos):
    return nltkpos == "n" and spacypos == "NOUN" or \
           nltkpos == "v" and spacypos == "VERB"

def map_to_synonyms(t, lang="spa"):

    "Map the token in 't' to synonyms for normalisation."

    token, result = t

    senses = set()

    for synset in wn.synsets(result, lang=lang):
        if compare_pos(synset.pos(), token.pos_):
            senses.add(synset.name())

    # Create a term with the senses found for the word.

    return token, Term(result, senses)

# Internal functions for setting up and finalising results.

def init_result(token):

    """
    Return a tuple containing 'token' and the initial result involving 'token'.
    """

    return (token, token.text)

def complete_result(t):

    "Return the eventual result from 't', this being (token, result)."

    token, result = t
    return result

# Fragment processing.

def process_fragment_tokens(fragments, ops):

    "Process the 'fragments' using the given 'ops'."

    for fragment in fragments:
        fragment.words = process_tokens(fragment.get_text(), [init_result] + ops + [complete_result])

# vim: tabstop=4 expandtab shiftwidth=4
