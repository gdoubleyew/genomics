#!/bin/bash
# Run tests of the seek database and compare against known result

# Set up env from qian.init2
cur=/Genomics/ogtr03/qzhu/usr4.9
export LD_LIBRARY_PATH=$cur/lib:$cur/lib64:/Genomics/ogtr03/qzhu/usr/lib:/Genomics/ogtr03/qzhu/usr/lib64:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=$cur/lib/pkgconfig/
export PATH=$cur/bin:$PATH
pytools=/r04/gwallace/src/genomics/pytools

# Get query file parameter
if [ "$1" == "" ]; then
  echo "Must specify query file as parameter, one query string per line."
  exit -1
fi

query_file=$1
gold_file=${query_file/query/gold}
echo "using query file $query_file, goldStd file $gold_file"

# Create a temp directory
tmp_dir=$(mktemp -d -t seek_test-$(date +%Y-%m-%d-%H-%M-%S)-XXXX)
# tmp_dir=/tmp/seek_test-2020-05-15-13-06-39-EZCP

# Step 1 Run the queries
if true; then
  pushd /data/seek/Seek
  # Run the query - produces binary file results
  time /Genomics/Users/qzhu/sleipnir_build/bin/SeekMiner -x dataset.map -i gene_map.txt -d db.combined -p prep.combined -P platform.combined -Q quant2 -n 1000 -b 200 -u sinfo.combined -R dataset_size -V CV -m -M -O -q $query_file -o $tmp_dir
  # Finished running query
  popd
fi

source ~/.bashrc
conda activate genomics
# Step 2 Evaluate the precision at each recall depth
if true; then
  python $pytools/eval_precison.py -t human -s /Genomics/ogtr03/qzhu/seek_sleipnir_build/bin -g $gold_file -q $query_file -o $tmp_dir 2> $tmp_dir/out.precision.txt
fi

# Step 3 Compare the result to the expected result
# TODO

# Step 4 Optional - check the precision of one query line
if false; then
  conda activate genomics
  # Can create a loop here
  i=1
  # Output the binary file gscore results to a text file
  python /Genomics/ogtscratch/tmp/qzhu/modSeek/show_seek_results.py human /Genomics/ogtr03/qzhu/seek_sleipnir_build/bin $tmp_dir/$i.query genes 2> $tmp_dir/$i.gene_result.txt
  # run the validation
  python $pytools/validate_precision.py -r $tmp_dir/$i.gene_result.txt -g $tmp_dir/$i.gold -a $tmp_dir/out.precision.txt -i $i
fi
