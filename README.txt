= Introduction =

This is a software distribution for processing textual fragments prepared from
audio recording transcripts, comparing the fragments for similarity and
suggesting connections between the fragments.

== Getting Started ==

To be able to use this software, appropriate data is required along with the
means to run the software. See the [[#Required Data]] and [[#Required
Software]] sections for more details.

To actually run the software, a command of the following form should work:

./fragments.py OUTPUT DATA/*.xml

Here, a directory for output data is supplied as OUTPUT. Meanwhile, input data
is specified as residing in the DATA directory, with this directory needing to
be initialised by the user before running the above command.

== Required Data ==

A collection of XML files describing the transcripts are required to produce
output data using this software. These files must employ filenames of the
following general form:

<prefix>_<datatype>.xml

Here, <prefix> is a descriptive label perhaps indicating something about the
original audio recording. Meanwhile, <datatype> must contain one of the
supported data types, which are the following:

Text
Tiers

Related files must share the same filename prefix. For example:

A1_AllText.xml
A1_AllTiers.xml

Here, a prefix of "A1" indicates that the files describe the same recording.
Meanwhile, the first filename includes "Text" and therefore provides textual
information, whereas the second filename includes "Tiers" and therefore
provides "tier" information. These kinds of information and the accepted
format are described below.

=== XML Data Formats ===

One kind of XML file features "tier" information and provides hierarchical
category information applied to periods of audio in the following form:

<TIERS>
  <TIER columns="Parent">
    <span start="1.234" end="12.345"><v>Child</v></span>

Here, a period starting at 1.234 and ending at 12.345 is annotated with the
hierarchical category "Parent/Child".

The other kind of XML file features "text" information and provides textual
information corresponding to periods of audio, effectively supplying subtitles
for the audio content. It has the following form:

<TIERS>
  <TIER columns="Parent">
    <span start="2.500" end="2.840"><v>the</v></span>
    <span start="2.840" end="3.450"><v>first</v></span>
    <span start="3.450" end="4.000"><v>day</v></span>

Here, three periods, the first of which starting at 2.500 and the last of
which ending at 4.000 provide the words "the first day".

== Required Software ==

The software is written in the Python programming language, tested with Python
2.7, and makes use of a number of additional packages or libraries. These are
presented below in their own distinct sections.

=== NLTK ===

Required components:

 * nltk (the package itself)
 * omw (Open Multilingual WordNet)
 * stopwords

Installing the software and data:

{{{
python -m pip install -U --user nltk
python -c 'import nltk; nltk.download("wordnet")'
python -c 'import nltk; nltk.download("omw")'
python -c 'import nltk; nltk.download("stopwords")'
}}}

=== spaCy ===

Required components:

 * spaCy (the package itself)
 * es (Spanish data model)

Installing the software and data:

{{{
python -m pip install -U --user spacy
python -m spacy download es --user
}}}
