#!/usr/bin/bash
pytools="/Users/gwallace/src/github/gdoubleyew/genomics/pytools"
results="/Users/gwallace/src/github/FunctionLab/data/results"

files=("q20_40r10.txt" "q40_100r10.txt" "q100_300r10.txt" "precision_vs_depth.txt")

for f in ${files[*]}; do
  echo $f
  python $pytools/compare_result_files.py -a $results/bioinform_long/out/$f -b $results/bioinform1/out/$f
done
