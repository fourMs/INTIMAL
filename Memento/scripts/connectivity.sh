#!/bin/sh

# Show fragments with a number of relations other than that expected.

OUTPUT=${1:-OUTPUT}
KIND=${2:-forward}
NUM=${3:-3}

for FN in "$OUTPUT"/data/*/"$KIND" ; do
    if [ `ls -1 "$FN" | wc -l` != "$NUM" ] ; then
        DN=`dirname "$FN"`
        echo `basename "$DN"`
    fi
done
