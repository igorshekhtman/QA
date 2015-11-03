#!/bin/sh
#
# right now this will just go though list of files in this directory, but no
# reason we cannot extend it later to take a path or a directory
#
# NOTE: 
server=$1
if [[ -z $1 ]]; then
    echo "arg1 is server name not provided"
    exit 2
else
    server=$1
fi

for i in *.txt; do
    file=$(basename $i)
    cohort_id=${file%.*}
    Echo ""
    echo "uploading for $cohort_id"
    curl -X POST -H "Content-Type: text/html; charset=utf-8" --data-binary "@$i" http://$server:8765/trie/install/10000353
    #curl -X POST -H "Content-Type: text/html; charset=utf-8" --data-binary "@$i" http://$server:8765/trie/install/10000469
    #curl -X POST -H "Content-Type: text/html; charset=utf-8" --data-binary "@$i" http://$server:8765/trie/install/$cohort_id
done
echo "finsished!"
