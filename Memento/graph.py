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
%s fragments {
    node [shape=ellipse];
%s
%s
}
"""

node_template = """\
    %s [label="%s",color="%s",style=filled,fillcolor="%s"];
"""

edge_template = """\
    %s -- %s [len="%s",color="%s"];
"""

directed_edge_template = """\
    %s -> %s [len="%s",color="%s"];
"""

def write_graph(relations, filename, directed=True, labels=False):

    """
    Write a graph featuring the given 'relations' mapping from fragments to
    connections, producing a file with the given 'filename'.
    """

    out = codecs.open(filename, "w", encoding="utf-8")
    try:
        # Determine the unreachable nodes.

        reachable = set()

        for fragment, connections in relations.items():
            for connection in connections:
                reachable.add(connection.relation(fragment))

        unreachable = set(relations.keys()).difference(reachable)
        unreachable_relations = set()

        # Produce edge definitions using the template.

        edges = []
        for fragment, connections in relations.items():
            colour = fragment in unreachable and "#00000077" or "#00000011"

            for connection in connections:
                related = connection.relation(fragment)

                # Record related fragments for unreachable ones.

                if fragment in unreachable:
                    unreachable_relations.add(related)

                # Define the edge.

                edges.append((directed and directed_edge_template or edge_template) %
                             (id(fragment),
                              id(related),
                              connection.measure(),
                              colour))

        # Produce node definitions using the template.

        nodes = []

        for fragment in relations.keys():

            # Only label unreachable fragments.

            if fragment in unreachable:
                label = labels and fragment.label().replace(":", "\\n") or ""
                colour = "#000000ff"
                fill_colour = "#ff0000ff"
            elif fragment in unreachable_relations:
                label = ""
                colour = "#00000077"
                fill_colour = "#ff000033"
            else:
                label = ""
                colour = "#00000077"
                fill_colour = "none"

            # Define the node.

            nodes.append(node_template % (id(fragment), label, colour, fill_colour))

        # Produce a graph description, combining the node and edge definitions.

        print >>out, graph_template % (directed and "digraph" or "graph",
                                       "".join(nodes),
                                       "".join(edges))

    finally:
        out.close()

# vim: tabstop=4 expandtab shiftwidth=4
