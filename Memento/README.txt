# Introduction

This is a software distribution for processing textual fragments prepared from
audio recording transcripts, comparing the fragments for similarity and
suggesting connections between the fragments.

More information can be found in the docs directory in this distribution.

 * For reading in a text editor, see docs/wiki/Introduction
 * For reading in a Web browser, see docs/html/index.html

## A Note about the Documentation

The original content in docs/wiki aims to be readable as plain text under most
circumstances, but the intention is that this content be translated to HTML
since it employs a formatting language based on the MoinMoin wiki format
syntax.

The following command can be used to generate the HTML form of the
documentation from the main directory of this distribution:

moinconvert --input-dir docs/wiki --document-index index.html \
            --output-dir docs/html --theme mercurial \
            --macros --root Introduction --all
