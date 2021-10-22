#!/usr/bin/env bash
# Duplicates the input CSV file (argument 1) N times (argument 2) into a single giant dataset.
# Assumes that the CSV has a header row.
# The result is stored in "dup_$N_$INPUT.csv"

IN_CSV="$1"
N="$2"
OUT_CSV="dup_${N}_${IN_CSV}"

HEADER=$(head -n1 ${IN_CSV})
tail -n +2 ${IN_CSV} > tmp.csv
CATARGS=$(printf 'tmp.csv %.0s' `seq 1 $N`)

#echo $HEADER
echo "$HEADER" > "$OUT_CSV"
#echo $CATARGS
cat $CATARGS >> "$OUT_CSV"

rm tmp.csv

