#!/bin/sh

# Show the range of measures for fragment similarity.

OUTPUT=${1:-OUTPUT}
KIND=${2:-translation}

  ls -1 "$OUTPUT"/data/*/"$KIND"/*/measure \
| xargs -I{} sh -c "cat '{}' ; echo $'\t{}'" \
| sort -n -k1
