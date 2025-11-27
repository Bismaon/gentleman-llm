#!/usr/bin/env bash

mkdir -p old

for file in results/*_*.txt; do
    base=$(basename "$file")
    name="${base%_*}"           # remove version (_x.txt)
    num="${base##*_}"           # get version (x.txt)
    num="${num%.*}"             # get version number (x)

    # find all versions of this filename
    versions=(results/"$name"_*.txt)

    # find last version of this filename
    max_file=""
    max_num=-1
    for v in "${versions[@]}"; do
        vnum=$(basename "$v")
        vnum="${vnum##*_}"
        vnum="${vnum%.*}"
        if (( vnum > max_num )); then
            max_num=$vnum
            max_file="$v"
        fi
    done

    # keep last version
    for v in "${versions[@]}"; do
        if [[ "$v" != "$max_file" ]]; then
            mv "$v" old/
        fi
    done
done
