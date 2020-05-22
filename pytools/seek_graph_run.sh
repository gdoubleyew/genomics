#!/bin/bash
# Reproduce the graphs (supplemental figures 1a and 1c) from the seek paper.

gdir="/data/gwallace/seek"
seekdir="/data/gwallace/seek/Seek"
setdir="/Genomics/ogtscratch/tmp/qzhu/modSeek/setting/human"
pytools="/r04/gwallace/src/genomics"

# for group sizes 20-40 select query strings of size 2-10 (by 2s)
# for group sizes 40-100 select query strings of size 2-20 (by 2s)
# for group sizes 100-300 select query strings of size 2-20 (by 4s)
qgroups=("q20_40" "q40_100" "q100_300")
qcounts=("2,4,6,8,10" "2,4,6,8,10" "2,6,10,14,18")
qmins=(20 40  100)
qmaxs=(40 100 300)

source ~/.bashrc

# Produce the query files and gold standard files
if false; then
  if [ -z $CONDA_DEFAULT_ENV ] || [ $CONDA_DEFAULT_ENV != "genomics" ]; then
    conda activate genomics
  fi
  for i in ${!qgroups[@]}; do
    echo "${qgroups[$i]} ${qcounts[$i]}"
    cmd="$pytools/create_queries.py -min ${qmins[$i]} -max ${qmaxs[$i]} \
      -c ${qcounts[$i]} -o $gdir/queries/${qgroups[$i]} -i $gdir/human_go_slim.gmt"
    echo $cmd
    python $cmd
    # python $gdir/src/pytools/create_queries.py -min 40 -max 100 -c 2,4,6,8,10 -o $gdir/queries/q40_100 -i $gdir/human_go_slim.gmt
    # python $gdir/src/pytools/create_queries.py -min 100 -max 300 -c 2,6,10,14,18 -o $gdir/queries/q100_300 -i $gdir/human_go_slim.gmt
  done
fi

# Run the queries using SeekMiner for each sub-group in a different output directory (time process)
if false; then
  pushd $seekdir
  source seek_env
  for group in ${qgroups[*]}; do
    echo "################# running group $group #################"
    query_file=$gdir/queries/$group.query.txt
    result_dir=$gdir/results/$group
    # Run the query - produces binary file results
    time ./bin/SeekMiner -x dataset.map -i gene_map.txt -d db.combined \
      -p prep.combined -P platform.combined -Q quant2 -u sinfo.combined -n 1000 -b 200  \
       -R dataset_size -V CV -I LOI -z z_score -m -M -O -q $query_file -o $result_dir
    # Finished running query
  done
  popd
fi

# Genereate filelists need for SeekEvaluator
if false; then
  if [ -z $CONDA_DEFAULT_ENV ] || [ $CONDA_DEFAULT_ENV != "genomics" ]; then
    conda activate genomics
  fi
  # Create the individual query gold standard files in the results directory
  # import eval_precison as ep
  # gold = ep.read_genes("/data/gwallace/seek/queries/q20_40.goldStd.txt")
  # ep.write_goldstd(gold, "/data/gwallace/seek/results/q20_40/")
  for group in ${qgroups[*]}; do
    rdir=$gdir/results/$group
    gfile=$gdir/queries/${group}.goldStd.txt
    python $pytools/create_goldstd_files.py -g $gfile -o $rdir
  done

  # Create the filelists for use by SeekEvaluator
  for group in ${qgroups[*]}; do
    python $pytools/create_eval_filelists.py \
      -i /data/gwallace/seek/results/$group \
      -o /data/gwallace/seek/results/$group \
      -g /Genomics/ogtscratch/tmp/qzhu/modSeek/setting/human/genes.txt
  done
fi

# Run SeekEvaluator to get the precision at specified recall depth
#  it will generate the aggregate min/max and quartiles for each query size
if false; then
  pushd $seekdir
  source seek_env
  for i in ${!qgroups[@]}; do
    group=${qgroups[$i]}
    counts=${qcounts[$i]}
    rdir=$gdir/results/$group
    declare -a counts=($(echo $counts | tr "," " "));
    for n in ${counts[*]}; do
    # TODO, also for 2,6,10,14,18
      echo "" > $rdir/result_qcount.$n
      # Parameters are: -M multiquery, -B (agg_quartile) min/max quartiles,
      # --pr precision at x depth, --x_per recall depth or pr in percent, -f fold over random
      # For fold_over_random I'm not sure why it doesn't divide by change of random choice * recall depth.
      ./bin/SeekEvaluator -S $rdir/filelist_q$n.gold -G $rdir/filelist_q$n.gscore \
      -Q $rdir/filelist_q$n.query -X $rdir/filelist_q$n.exclude \
      -Y $rdir/filelist_q$n.include -i $setdir/gene_map.txt \
      -d /tmp/out -M -B --pr -f --x_per 0.1 >> $rdir/result_qcount.$n
    done
  done
  popd
fi

# 4 - Create the precision over recall plot. Run SeekEvaluator again with different options
#    - using pr_all, and then other options as the same.