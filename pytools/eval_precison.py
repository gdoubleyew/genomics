#!/usr/bin/python

'''
Script created by modifying scripts show_query_score.py and show_seek_results.py.
This script evaluates each query with respect to the gold standard results for the query.
It prints the precision at the depth for each gene recalled (from the gold standard).
For example if there were 10 genes in a group and 2 of them used for the query string, then
it would print 8 float values representing the precision at the point in the results
corresponding to each of the 8 genes we are trying to find.
Adapted by: gwallace
'''

import os
import sys
import argparse
sys.path.append(os.path.dirname(__file__))
from utils import read_genes, write_goldstd


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument('--organism', '-t', type=str, default='human',
                           help='organism type, default=human')
    argParser.add_argument('--sleipnir-path', '-s', type=str, required=True,
                           help='path to sleipnir bin directory')
    argParser.add_argument('--gold-std-file', '-g', type=str, required=True,
                           help='file with lists of gold standard genes, one list per line')
    argParser.add_argument('--query-file', '-q', type=str, required=True,
                           help='file with lists of query genes, one list per line')
    argParser.add_argument('--result-dir', '-o', type=str, required=True,
                           help='directory where result files will be written')
    args = argParser.parse_args()

    setting_dir = "/Genomics/ogtscratch/tmp/qzhu/modSeek"
    organism = args.organism
    sleipnir_path = args.sleipnir_path
    gold_std_file = args.gold_std_file
    query_file = args.query_file
    result_dir = args.result_dir

    for i in [sleipnir_path, setting_dir]:
        if not os.path.isdir(i):
            sys.stderr.write("Error: directory %s is not found\n" % i)
            sys.exit(1)

    if not os.path.exists(query_file):
        sys.stderr.write("Error, file %s does not exist!\n" % query_file)
        sys.exit(1)

    if not os.path.exists(gold_std_file):
        sys.stderr.write("Error, file %s does not exist!\n" % gold_std_file)
        sys.exit(1)

    setting_dir = os.path.abspath(setting_dir)
    query_file = os.path.abspath(query_file)
    gold_std_file = os.path.abspath(gold_std_file)

    gene_file = setting_dir + "/setting/" + organism + "/genes.txt"
    gene_map = setting_dir + "/setting/" + organism + "/gene_map.txt"
    dset_plat = setting_dir + "/setting/" + organism + "/new.%s.dset.list" % organism
    null_file = setting_dir + "/null"
    exclude_file = null_file

    # The gold standard genes are in a single file for all queries, but for SeekEvaluator
    #  we need a file per query with the gold standard genes and ideally in the results dir
    gold_std_genes = read_genes(gold_std_file)
    write_goldstd(gold_std_genes, result_dir)

    queries = read_genes(query_file)

    for i in range(len(queries)):
        query_file = os.path.join(result_dir, "{}.query".format(i))
        goldref_file = os.path.join(result_dir, "{}.gold".format(i))
        gene_score_file = os.path.join(result_dir, "{}.gscore".format(i))
        dataset_weight_file = os.path.join(result_dir, "{}.dweight".format(i))
        for f in [query_file, gene_score_file, dataset_weight_file]:
            if not os.path.exists(f):
                sys.stderr.write("Error: file {} not found\n".format(f))
                sys.exit(-1)
        # build and run the command per query
        cmd = "%s/SeekEvaluator -O --pr_all -i %s -y %s -U %s -d %s " % \
            (sleipnir_path, gene_map, null_file, gene_file, result_dir) + \
            "-s %s -g %s -q %s" % \
            (goldref_file, gene_score_file, query_file)
        # print(cmd)
        os.system(cmd)
#
#    scores = []
#    f = open("%s/all_query_scores.txt" % temp_dir)
#    for l in f:
#        l = l.rstrip("\n")
#        scores.append(float(l))
#    f.close()
#    for i in range(len(queries)):
#        sc = sum([scores[j] for j in q_map[i]])
#        sys.stdout.write("%.5f\n" % sc)
#
#    os.system("rm -rf %s" % temp_dir)
