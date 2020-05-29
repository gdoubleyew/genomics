#!/bin/bash
# Reproduce the graphs (supplemental figures 1a and 1c) from the seek paper.

gdir="/data/gwallace/seek"
seekdir="/data/gwallace/seek/Seek"
setdir="/Genomics/ogtscratch/tmp/qzhu/modSeek/setting/human"
pytools="/r04/gwallace/src/genomics/pytools"

recall_pct=0.1
# gmt_file="$gdir/human_go_slim.gmt"
gmt_file="$gdir/qian_go_slim.gmt"

# for group sizes 20-40 select query strings of size 2-10 (by 2s)
# for group sizes 40-100 select query strings of size 2-20 (by 2s)
# for group sizes 100-300 select query strings of size 2-20 (by 4s)
qgroups=("q20_40" "q40_100" "q100_300")
qcounts=("2,4,6,8,10" "2,6,10,14,18" "2,6,10,14,18")
qmins=(20 40  100)
qmaxs=(40 100 300)

# check if directories exist
if [ ! -d $gdir ] || ! [ -d $seekdir ]; then
  echo "Directory doesn't exist $gdir or $seekdir"
  exit -1
fi

function check_dir() {
  if [ ! -d $1 ]; then
    mkdir -p $1
  fi
}

source ~/.bashrc
if [ -z $CONDA_DEFAULT_ENV ] || [ $CONDA_DEFAULT_ENV != "genomics" ]; then
  conda activate genomics
fi

# Step 1: Produce the query files and gold standard files
if true; then
  check_dir "$gdir/queries"
  for i in ${!qgroups[@]}; do
    echo "${qgroups[$i]} ${qcounts[$i]}"
    cmd="$pytools/create_queries.py -min ${qmins[$i]} -max ${qmaxs[$i]} \
      -c ${qcounts[$i]} -o $gdir/queries/${qgroups[$i]} -i $gmt_file"
    echo $cmd
    python $cmd
  done
fi

# Step 2: Run the queries using SeekMiner for each sub-group in a different output directory (time process)
if true; then
  pushd $seekdir
  source seek_env
  for group in ${qgroups[*]}; do
    echo "################# running group $group #################"
    query_file=$gdir/queries/$group.query.txt
    result_dir=$gdir/results/$group
    check_dir $result_dir
    # Run the query - produces binary file results
    time ./bin/SeekMiner -x dataset.map -i gene_map.txt -d db.combined \
      -p prep.combined -P platform.combined -Q quant2 -u sinfo.combined -n 1000 -b 200  \
       -R dataset_size -V CV -I LOI -z z_score -m -M -O -q $query_file -o $result_dir
    # Finished running query
  done
  popd
fi

# Step 3: Genereate filelists need for SeekEvaluator
if true; then
  # Create the individual query gold standard files in the results directory
  for group in ${qgroups[*]}; do
    rdir=$gdir/results/$group
    gfile=$gdir/queries/${group}.goldStd.txt
    echo "Write goldstd files for group $group"
    python $pytools/create_goldstd_files.py -g $gfile -o $rdir
  done

  rdir=$gdir/results
  # Create the filelists for use by SeekEvaluator plot 1a
  for group in ${qgroups[*]}; do
    echo "Create filelists for group $group"
    python $pytools/create_plot1a_filelists.py \
      -i $rdir/$group \
      -o $rdir/$group \
      -g /Genomics/ogtscratch/tmp/qzhu/modSeek/setting/human/genes.txt
  done

  # Create the filelists for use by SeekEvaluator plot 1c
  rdir=$gdir/results
  python $pytools/create_plot1c_filelists.py \
    -i $rdir/q20_40,$rdir/q40_100,$rdir/q100_300 \
    -o $rdir \
    -g /Genomics/ogtscratch/tmp/qzhu/modSeek/setting/human/genes.txt
fi

# Step 4: Run SeekEvaluator to get the aggregate precision at different query sizes
#  it will generate the aggregate min/max and quartiles for each query size for plot 1a
if true; then
  pushd $seekdir
  source seek_env
  for i in ${!qgroups[@]}; do
    group=${qgroups[$i]}
    counts=${qcounts[$i]}
    rdir=$gdir/results/$group
    declare -a counts=($(echo $counts | tr "," " "));
    echo "Running SeekEvaluator for group $group"
    for n in ${counts[*]}; do
      outfile=$rdir/result_qgroup.$n
      # truncate the output file
      echo -n > $outfile
      # Parameters are: -M multiquery, -B (agg_quartile) min/max quartiles,
      # --pr precision at x depth, --x_per recall depth or pr in percent, -f fold over random
      ./bin/SeekEvaluator -S $rdir/filelist_q$n.gold -G $rdir/filelist_q$n.gscore \
      -Q $rdir/filelist_q$n.query -X $rdir/filelist_q$n.exclude \
      -Y $rdir/filelist_q$n.include -i $setdir/gene_map.txt \
      -d /tmp/out -M -B --pr -f --x_per $recall_pct &>> $outfile
    done
  done
  popd
fi

# Run SeekEvaluator to get the aggregate precision at different recall depths
#  it will generate the aggregate min/max and quartiles for each query size for plot 1c
if true; then
  pushd $seekdir
  source seek_env
  rdir=$gdir/results
  recall_depths=(.01 .02 .04 .06 .08 .1 .2 .4 .6 .8 1)
  for depth in ${recall_depths[*]}; do
    echo "Running SeekEvaluator for depth $depth"
    depth_pct=$(echo "$depth * 100 / 1" | bc)
    outfile=$rdir/result_recall_curve.$depth_pct
    # truncate the output file
    echo -n > $outfile
    # Parameters are: -M multiquery, -B (agg_quartile) min/max quartiles,
    # --pr precision at x depth, --x_per recall depth or pr in percent, -f fold over random
    ./bin/SeekEvaluator -S $rdir/filelist_seek1c.gold -G $rdir/filelist_seek1c.gscore \
    -Q $rdir/filelist_seek1c.query -X $rdir/filelist_seek1c.query \
    -Y $rdir/filelist_seek1c.include -i  $setdir/gene_map.txt \
     -d /tmp/out -M -B --pr -f --x_per $depth &>> $outfile
  done
  popd
fi

# Step 5: Create the precision over recall plot.
if true; then
  outdir=$gdir/results/out
  for group in ${qgroups[*]}; do
    rdir=$gdir/results/$group
    check_dir $outdir
    python $pytools/plot_seek1a.py -i $rdir -o $outdir -p $recall_pct
  done

  rdir=$gdir/results
  python $pytools/plot_seek1c.py -i $rdir -o $outdir
fi


# Run SeekEvaluator again with different options
#    - using pr_all, and then other options as the same.
