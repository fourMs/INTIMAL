#!/usr/bin/env python
# -*- coding: utf-8

"""
Production of graphs describing fragments and their relationships.

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
            edges.append(edge_template % (id(connection.fragments[0]),
                                          id(connection.fragments[1]),
                                          connection.label(),
                                          connection.label()))

        # Produce a graph description, combining the node and edge definitions.

        print >>out, graph_template % ("".join(nodes), "".join(edges))

    finally:
        out.close()

# vim: tabstop=4 expandtab shiftwidth=4
