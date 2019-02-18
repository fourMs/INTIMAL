#!/usr/bin/env python
# -*- coding: utf-8

"""
Selection of related fragments.
"""

from collections import defaultdict

# Connection-related operations.

class ConnectedFragment:

    "A record of fragment relationships via connections."

    def __init__(self, fragment, connections):
        self.fragment = fragment
        self.connections = connections

    def __iter__(self):
        return RelatedFragments(self.fragment, self.connections)

class RelatedFragments:

    "A provider of related fragments from connections."

    def __init__(self, fragment, connections):
        self.fragment = fragment
        self.connection_iter = iter(connections)

    def next(self):

        "Return the next related fragment with its connection."

        while self.connection_iter:
            try:
                connection = self.connection_iter.next()
                return connection.relation(self.fragment), connection
            except StopIteration:
                self.connection_iter = None

        raise StopIteration

def get_related_fragments(connections):

    """
    Return a mapping from fragments to connections for the given 'connections'.
    """

    d = defaultdict(list)

    for connection in connections:
        for fragment in connection.fragments:
            d[fragment].append(connection)

    return d

def select_related_fragments(related, num, get_criteria):

    """
    For each fragment in the 'related' mapping, select related fragments having
    'num' different values, with each value obtained by calling the given
    'get_criteria' function.
    """

    d = defaultdict(list)

    for fragment, connections in related.items():
        values = set()
        values.add(get_criteria(fragment, values))

        # Obtain each related fragment, assessing it with the function.

        for related, connection in ConnectedFragment(fragment, connections):
            if len(values) >= num:
                break

            value = get_criteria(related, values)

            if value:
                d[fragment].append(connection)
                values.add(value)

    return d

def select_related_fragments_by_category(related, num):

    """
    For each fragment in the 'related' mapping, select related fragments from
    the same parent category but with 'num' different subcategories.
    """

    return select_related_fragments(related, num, get_distinct_subcategory)

def select_related_fragments_by_participant(related, num):

    """
    For each fragment in the 'related' mapping, select related fragments from
    'num' different participants.
    """

    return select_related_fragments(related, num, get_distinct_participant)

def sort_related_fragments(related):

    "Sort the 'related' fragments in descending order of similarity."

    for fragment, connections in related.items():
        connections.sort(key=lambda x: x.measure(), reverse=True)

# Fragment criteria helper functions.

def get_distinct_participant(fragment, values):

    """
    From 'fragment' select the participant, returning it if it is not in
    'values', returning None otherwise.
    """

    participant = fragment.source.participant()

    if participant not in values:
        return participant
    else:
        return None

def get_distinct_subcategory(fragment, values):

    """
    From 'fragment' select a category  subcategory, returning it if it is not in
    'values', returning None otherwise.
    """

    category = fragment.category
    first = values and list(values)[0] or None
    parent = first and first.parent or None

    # The parent category must match the existing categories.

    if not parent or category.parent == parent and category not in values:
        return category
    else:
        return None

# vim: tabstop=4 expandtab shiftwidth=4
