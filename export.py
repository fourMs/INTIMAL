#!/usr/bin/env python2.7
# -*- coding: utf-8

"""
Collect sorted relations between fragments according to different selection
criteria.

Produce reports and structured data describing the processed data.
"""

# Input and output.

from inputs import get_flag, get_option, get_options

from serialised import get_serialised_connections, get_serialised_fragments

from wordlist import get_wordlist_from_file

import outputs

import os, sys

# Abstractions and relation processing.

from objects import process_fragments, \
                    process_term_vectors, \
                    recompute_connections

from related import get_accessing_fragments, \
                    combine_related_fragments, \
                    find_all_fragments, \
                    get_related_fragments, \
                    get_related_fragment_selectors, \
                    related_fragment_selectors, \
                    select_related_fragments, \
                    sort_related_fragments

from stats import emit_statistics_output, process_statistics



# Restoration of serialised data.

def restore_fragments(out):

    "Restore fragments from an output file via 'out'."

    out["fragments"] = fragments = \
        get_serialised_fragments(outfile("fragments.txt"))

    return fragments

def restore_connections(fragments, config, out):

    """
    Using 'fragments' and 'config' to adjust the processing, restore connections
    from an output file via 'out'.
    """

    # Define the term vectors.

    process_term_vectors(fragments, not config.get("term_presence_only"),
                         out["inv_doc_frequencies"])

    # Restore the connections using the fragments.

    out["connections"] = connections = \
        get_serialised_connections(outfile("connections.txt"), fragments)

    # Recompute the similarities.

    connections = recompute_connections(connections)

    return connections



# Word filtering/selection.

def process_wordlist(fragments, config, out):

    "Process 'fragments'"

    if config.get("wordlist"):
        process_fragments(fragments, [config.get("wordlist").filter_words])

        # Register the filtered output. Note that the fragments are mutated,
        # so the original fragment output would also be filtered at this point.

        out["fragments_filtered"] = fragments

# Relation processing.

def process_relations(connections, config, out):

    """
    Process 'connections' to obtain relations, using 'config' to adjust the
    processing, registering output with 'out'.
    """

    related = get_related_fragments(connections)

    # Impose an ordering on the related fragments.

    sort_related_fragments(related)

    # Only restrict the related fragments if requested.

    if not config.has_key("select"):
        return related

    num = config.get("num_related_fragments")
    all_related = []

    # For each set of selection criteria, select appropriate fragments.

    for criteria in config.get("select"):

        # Handle the special case "all".

        if criteria == "all":
            for criteria, selectors in related_fragment_selectors.items():
                all_related.append((criteria, select_related_fragments(related, num, selectors)))
            continue

        # Obtain the functions from their names.

        names = criteria.split(",")
        selectors = get_related_fragment_selectors(names)

        # Select and store the related fragments.

        all_related.append((criteria, select_related_fragments(related, num, selectors)))

    out["all_related"] = all_related

    return related

def process_accessibility(fragments, out):

    """
    For all 'fragments', assess their accessibility using related fragment
    information from 'out'.
    """

    # Get the related fragment mapping from (criteria, mapping) tuples.

    all_related = map(lambda i: i[1], out["all_related"])

    # Combine the mappings to obtain relationships.

    combined = combine_related_fragments(all_related)

    # Obtain the accessibility map for each fragment.

    out["accessibility"] = find_all_fragments(fragments, combined)

    # Obtain the mapping from fragments to those accessing them.

    accessing = get_accessing_fragments(combined)

    # Obtain the unreachable fragments. These would be suitable starting points.

    out["unreachable"] = set(fragments).difference(accessing.keys())



# Output data production.

def emit_filtered_output(out):

    "Using 'out', emit filtered output data featuring the processed input."

    outfile = out.filename

    # Emit the fragments for inspection and potential recovery.

    if out.has_key("fragments_filtered"):
        outputs.show_fragments(out["fragments_filtered"], outfile("fragments_filtered.txt"))

def emit_relation_output(out):

    "Using 'out', emit relation output."

    outfile = out.filename
    datasets = out.get("all_related")

    if not datasets:
        return

    # Emit related data.

    for criteria, dataset in datasets:
        outputs.show_related_fragments(dataset, outfile(criteria))

    outputs.write_fragment_data(datasets, outfile("data"))

    # Emit an accessibility report for fragments.

    outputs.show_fragment_accessibility(out["accessibility"], outfile("accessibility"))
    outputs.show_all_words(out["unreachable"], outfile("unreachable"))



# Help text for program invocation.

progname = os.path.split(sys.argv[0])[-1]

related_fragment_selectors_list = list(related_fragment_selectors.keys())
related_fragment_selectors_list.sort()

related_fragment_selectors_text = "\n".join(related_fragment_selectors_list)

helptext = """\
Usage: %s [ <options> ] <output directory>

An output directory name is needed for producing output files and to read
data previously processed by the build program.

Input file processing options:

--word-list <filename>  Preserve only words found in the indicated file, these
                        being the root forms of word families (for example,
                        general verbs instead of conjugations)

Output options:

--no-output             Suppress output for testing purposes

--num-related <number>  Indicate the maximum number of related fragments to be
                        produced for each fragment

--select <criteria>     Select related fragments using the given criteria, these
                        being a comma-separated list of functions, described
                        below

--stats                 Produce output featuring statistical reports

--term-presence-only    Do not employ term frequencies in term vectors

Related fragments can be selected by combining criteria specified using a list
of functions chosen from the following:

%s

Specifying "all" will generate related fragments for all of these functions.

The output directory will be populated with files containing the following:

 * fragments and related fragments

The output directory will also contain a data subdirectory containing the
processed data in a structured form.

If --stats is indicated, the following statistical reports are produced:

 * category fragments (fragments found in each category)
 * category terms (terms found in each category)
 * common category terms (categories associated with each term)
 * common fragment terms (fragments associated with each term)
 * term frequencies
 * term document frequencies
 * term inverse document frequencies
""" % (progname, related_fragment_selectors_text)



# Main program.

if __name__ == "__main__":

    # Show the help message if requested.

    if get_flag("--help"):
        print >>sys.stderr, helptext
        sys.exit(0)

    config = {}

    config["num_related_fragments"] = get_option("--num-related", 4, 4, int)
    config["select"] = get_options("--select")
    config["term_presence_only"] = get_flag("--term-presence-only")
    config["wordlist"] = get_wordlist_from_file(get_option("--word-list"))

    no_output = get_flag("--no-output")
    statistics_output = get_flag("--stats")

    # Obtain the output directory.

    try:
        outdir = sys.argv[1]

    # Show the help message and exit if the arguments are incorrect.

    except (IndexError, ValueError):
        print >>sys.stderr, helptext
        sys.exit(1)

    # Derive filenames for output files.

    out = outputs.Output(outdir)
    outfile = out.filename

    # Restore serialised data.

    fragments = restore_fragments(out)
    process_wordlist(fragments, config, out)
    process_statistics(fragments, out)
    connections = restore_connections(fragments, config, out)

    # Process relation data.

    process_relations(connections, config, out)
    process_accessibility(fragments, out)

    # Emit output.

    if not no_output:

        # Emit filtered output to show the effect of any word list.

        emit_filtered_output(out)

        # Emit relations for fragments.

        emit_relation_output(out)

        if statistics_output:
            emit_statistics_output(out)

# vim: tabstop=4 expandtab shiftwidth=4
