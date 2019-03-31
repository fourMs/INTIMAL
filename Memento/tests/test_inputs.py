#!/usr/bin/env python
# -*- coding: utf-8

"""
Test fragment construction.
"""

from test_support import set_verbose, show
from inputs import fill_categorised_fragments, get_categorised_fragments, \
                   populate_fragments
from objects import Category, Source
from xml.dom.minidom import parseString

# Test data.

tiers = """\
<TIERS>
  <TIER columns="Parent">
    <span start="1.234" end="3.456"><v>Category</v></span>
    <span start="3.456" end="6.789"><v>Category</v></span>
    <span start="6.789" end="12.345"><v>Different category</v></span>
  </TIER>
  <TIER columns="P">
    <span start="13.000" end="14.000"><v>C</v></span>
    <span start="16.000" end="18.000"><v>D</v></span>
  </TIER>
</TIERS>
"""

text = """\
<TIERS>
  <TIER columns="Speech">
    <span start="1.234" end="2.345"><v>Un</v></span>
    <span start="2.345" end="3.456"><v>día</v></span>
    <span start="3.456" end="4.567"><v>un</v></span>
    <span start="4.567" end="5.678"><v>pollo</v></span>
    <span start="5.678" end="6.789"><v>entra</v></span>
    <span start="6.789" end="7.890"><v>en</v></span>
    <span start="7.890" end="8.901"><v>un</v></span>
    <span start="8.901" end="10.123"><v>bosque</v></span>
    <span start="10.123" end="12.345"><v>.</v></span>
    <span start="12.345" end="13.000"><v>Una</v></span>
    <span start="13.000" end="14.000"><v>bellota</v></span>
    <span start="14.000" end="15.000"><v>cae</v></span>
    <span start="15.000" end="16.000"><v>en</v></span>
    <span start="16.000" end="17.000"><v>su</v></span>
    <span start="17.000" end="18.000"><v>cabeza</v></span>
    <span start="18.000" end="19.000"><v>.</v></span>
  </TIER>
</TIERS>
"""

# Test cases.

def test_categorised_fragments():
    categorised_fragments = get_categorised_fragments(parseString(tiers), "test")

    show("len(categorised_fragments)", len(categorised_fragments), 5)

    show("categorised_fragments[0].category",
         categorised_fragments[0].category, Category('Parent', 'Category'))
    show("categorised_fragments[0].source",
         categorised_fragments[0].source, Source("test", 1.234, 3.456))

    show("categorised_fragments[4].category",
         categorised_fragments[4].category, Category('P', 'D'))
    show("categorised_fragments[4].source",
         categorised_fragments[4].source, Source("test", 16.000, 18.000))

    filled = fill_categorised_fragments(categorised_fragments)
    show("len(filled)", len(filled), 8)

    show("filled[0].category", filled[0].category, None)
    show("filled[0].source", filled[0].source, Source("test", 0, 1.234))

    show("filled[6].category", filled[6].category, None)
    show("filled[6].source", filled[6].source, Source("test", 14.000, 16.000))

def test_populated_fragments():
    fragments = get_categorised_fragments(parseString(tiers), "test")
    populate_fragments(fragments, parseString(text), "test")

    show("len(fragments)", len(fragments), 5)

    show("len(fragments[0].words)", len(fragments[0].words), 2)
    show("len(fragments[1].words)", len(fragments[1].words), 3)
    show("len(fragments[2].words)", len(fragments[2].words), 4)

    show("fragments[0].words[0]", fragments[0].words[0], u"Un")
    show("fragments[2].words[-1]", fragments[2].words[-1], u".")
    show("fragments[4].words", fragments[4].words, [u"su", u"cabeza"])

def main():
    test_categorised_fragments()
    test_populated_fragments()

if __name__ == "__main__":
    set_verbose()
    main()

# vim: tabstop=4 expandtab shiftwidth=4
