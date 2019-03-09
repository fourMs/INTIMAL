#!/usr/bin/env python
# -*- coding: utf-8

"""
Selection of related fragments.
"""

from collections import defaultdict

# Connection-related operations.

def combine_related_fragments(all_related):

    """
    Combine mappings in 'all_related' to produce a single mapping from fragments
    to related fragments.
    """

    d = defaultdict(set)

    for mapping in all_related:
        for fragment, related in mapping.items():
            d[fragment].update(related)

    return d

def get_related_fragments(connections):

    """
    Return a mapping from fragments to connections for the given 'connections'.
    """

    d = defaultdict(list)

    for connection in connections:
        for fragment in connection.fragments:
            d[fragment].append(connection)

    return d

def select_related_fragments(related, num, criteria):

    """
    For each fragment in the 'related' mapping, select at most 'num' related
    fragments. Each selected fragment is assessed using the given list of
    'criteria' functions for association with the primary fragment.
    """

    d = defaultdict(list)

    for fragment, connections in related.items():

        # Start with the given fragment.

        fragments = [fragment]

        # Obtain each related fragment, assessing it with the function.

        for connection in connections:

            # Stop processing if the required number of fragments has been
            # reached.

            if len(fragments) >= num:
                break

            relation = connection.relation(fragment)

            # Assess the fragment using the criteria.

            for fn in criteria:
                if not fn(relation, fragments):
                    break

            # Where it meets all criteria, add it to the collection.

            else:
                d[fragment].append(connection)
                fragments.append(relation)

    return d

def sort_related_fragments(related):

    "Sort the 'related' fragments in descending order of similarity."

    for fragment, connections in related.items():
        connections.sort(key=lambda x: x.measure(), reverse=True)

# Fragment selection criteria functions.

def get_any_fragment(fragment, fragments):

    """
    For 'fragment', return a true value regardless of its relationship to
    'fragments'.
    """

    return True

def get_distinct_participant(fragment, fragments):

    """
    For 'fragment', return a true value if its participant is not already
    represented in 'fragments', returning a false value otherwise.
    """

    participant = fragment.source.participant()
    participants = map(lambda f: f.source.participant(), fragments)

    return participant not in participants

def get_distinct_subcategory(fragment, fragments):

    """
    For 'fragment', returning a true value if its subcategory is not already
    represented in 'fragments', all of which share the same parent category,
    returning a false value otherwise.
    """

    category = fragment.category
    parent = category.parent
    categories = map(lambda f: f.category, fragments)
    parents = map(lambda c: c.parent, categories)

    return parent in parents and category not in categories

def get_same_participant(fragment, fragments):

    """
    For 'fragment', return a true value if its participant is already
    represented in 'fragments', returning a false value otherwise. This should
    ensure that only a single participant is represented.
    """

    participant = fragment.source.participant()
    participants = map(lambda f: f.source.participant(), fragments)

    return participant in participants

# Registry of functions.

def get_related_fragment_selectors(names):

    "Return functions for the given 'names'."

    l = []
    for name in names:
        l += related_fragment_selectors[name]
    return l

related_fragment_selectors = {
    "any"           : [get_any_fragment],
    "translation"   : [get_distinct_participant],
    "rotation"      : [get_distinct_subcategory, get_same_participant],
    }

# Analysis functions.

def get_accessing_fragments(related):

    """
    Return a mapping from 'related' fragments to their accessors. This reverses
    the mapping from fragments to related fragments, permitting an assessment of
    how accessible related fragments are.
    """

    d = defaultdict(set)

    for primary, connections in related.items():
        for connection in connections:
            d[fragment.relation(primary)].add(primary)

    return d

def find_fragments(fragment, related, visited=None):

    "Return all fragments accessible from 'fragment' in 'related'."

    visited = visited or set()

    connections = related.get(fragment)

    if connections:
        for connection in connections:

            # Obtain each related fragment and search its relations if not
            # already visited.

            f = connection.relation(fragment)

            if f not in visited:
                visited.add(f)
                find_fragments(f, related, visited)

    return visited

# vim: tabstop=4 expandtab shiftwidth=4
