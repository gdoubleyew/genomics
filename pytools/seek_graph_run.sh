#!/bin/bash
# Reproduce the graphs (supplemental figures 1a and 1c) from the seek paper.

gdir="/data/gwallace/seek"
seekdir="/data/gwallace/seek/Seek"

# Steps
# 1 - Produce the query strings and gold standard files
#  - for group sizes 20-40 select query strings of size 2-10 (by 2s)
#  - for group sizes 40-100 select query strings of size 2-20 (by 2s)
#  - for group sizes 100-300 select query strings of size 2-20 (by 4s)
if false; then
  source ~/.bashrc
  conda activate genomics
  python $gdir/src/pytools/create_queries.py -min 20 -max 40 -c 2,4,6,8,10 -o $gdir/queries/q20_40 -i $gdir/human_go_slim.gmt
  python $gdir/src/pytools/create_queries.py -min 40 -max 100 -c 2,4,6,8,10 -o $gdir/queries/q40_100 -i $gdir/human_go_slim.gmt
  python $gdir/src/pytools/create_queries.py -min 100 -max 300 -c 2,6,10,14,18 -o $gdir/queries/q100_300 -i $gdir/human_go_slim.gmt
fi

# 2 - Run the queries using SeekMiner for each sub-group in a different output directory (time process)
if true; then
  pushd $seekdir
  source seek_env
  qgroups=("q20_40" "q40_100" "q100_300")
  for group in ${qgroups[*]}; do
    echo "################# running group $group ################# "
    query_file=$gdir/queries/$group.query.txt
    result_dir=$gdir/results/$group
    # Run the query - produces binary file results
    time ./bin/SeekMiner -x dataset.map -i gene_map.txt -d db.combined -p prep.combined -P platform.combined -Q quant2 -n 1000 -b 200 -u sinfo.combined -R dataset_size -V CV -I LOI -z z_score -m -M -O -q $query_file -o $result_dir
    # Finished running query
  done
  popd
fi

# 3 - Run SeekEvaluator to get the precision at each recall depth
#    - Consider using options
#      - pr' precision at depth',
#      - x_per' to specify a percent for pr'
#      - agg_quartile' to aggregate results by quartile (feed in all queries of size 2 etc)
#      - fold_over_random - will divide by the precision of a random choice.
        # But I'm not sure why it doesn't divide by change of random choice * recall depth.
#  These settings should give you everything you need to make the plot

# 4 - Create the precision over recall plot. Run SeekEvaluator again with different options
#    - using pr_all, and then other options as the same.
