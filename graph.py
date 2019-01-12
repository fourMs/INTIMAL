#!/usr/bin/env python
# -*- coding: utf-8

"""
Production of graphs describing fragments and their relationships.
"""

import codecs

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

    """
    Write a graph featuring the given 'fragments' and 'connections' to the
    specified 'filename'.
    """

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        # Produce node definitions using the template.

        nodes = []

        for fragment in fragments:
            nodes.append(node_template % (id(fragment), fragment.label()))

        # Produce edge definitions using the template.

        edges = []
        for connection in connections:
            edges.append(edge_template % (id(connection[0]), id(connection[1]), connection.label(), connection.label()))

        # Produce a graph description, combining the node and edge definitions.

        print >>out, graph_template % ("".join(nodes), "".join(edges))

    finally:
        out.close()

# vim: tabstop=4 expandtab shiftwidth=4
