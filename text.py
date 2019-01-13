#!/usr/bin/env python
# -*- coding: utf-8

"""
Elementary text handling.
"""

import unicodedata

# Word processing functions.

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

def is_punctuation(s):
    for c in s:
        if c not in punctuation:
            return False
    return True

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

# General text operations.

def match_tokens(tokens, words):

    "Match the given 'tokens' consecutively in the collection of 'words'."

    to_test = []

    # First, find places where the first token matches.

    for i, word in enumerate(words):
        if tokens[0] == word:
            to_test.append(i)

    # Then, investigate each of the possible matches.

    for i in to_test:
        to_match = tokens[1:]

        # For each subsequent word, match the next token.

        for word in words[i+1:]:
            if word == to_match[0]:
                del to_match[0]
                if not to_match:
                    return True
            else:
                break

    return False

def text_from_words(words):

    "Join 'words' in order to produce a reasonable text string."

    if not words:
        return ""

    l = [words[0]]

    for word in words[1:]:
        if not is_punctuation(word):
            l.append(" ")
        l.append(word)

    return "".join(l)

def to_text(i):

    "Return instance 'i' in textual form."

    if isinstance(i, (list, tuple)):
        return " ".join(map(to_text, i))
    else:
        return unicode(i).encode("utf-8")

# vim: tabstop=4 expandtab shiftwidth=4
