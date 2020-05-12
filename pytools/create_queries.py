"""
This scirpt takes in a .gmt file of correlated sets of genes and creates 3 output
files. 1) base.query.txt, 2) base.goldStd.txt, 3) base.group.txt. The query.txt
files has the query string genes, the goldStd has the corresponding correlated
genes that should be found by the query, and the group.txt identifies the .gmt
group that each query is based on. The query_pct values indicate what percentage
of the group genes to use as a query. You can specify multiple query_pct values
as a comma separated list or with mulitple -q args.
"""
import sys
import os
import re
import math
import random
import argparse
from structDict import StructDict


def parse_gmt(filename, min_gene_count, max_gene_count):
    """
    Parse a file that has a correlated gene group per line.
    Only keep groups that meet the min, max gene count criteria.
    """
    groups = []
    with open(filename, 'r') as fp:
        for line in fp:
            vals = line.rstrip(os.linesep).split("\t")
            group_id = vals[0]
            desc = vals[1]
            genes = vals[2:]
            mtch = re.search(r'\((\d+)\)', desc)
            if mtch is None:
                raise ValueError("Description missing gene count, {}".format(desc))
            num_genes = int(mtch.group(1))
            assert len(genes) == num_genes
            if num_genes >= min_gene_count and num_genes <= max_gene_count:
                group = StructDict({'id': group_id, 'desc': desc, 'genes': genes, 'size': num_genes})
                groups.append(group)
    return groups


def create_queries(groups, query_pct, outBaseFilename):
    """
    Create queries out of groups of biologically informative gene sets.
    Each group is a set of genes that are correlated with each other.
    One query line will be made for each query_pct in the list, the query_pct
    indicates what percentage of the gene group to use as the query, the rest
    will be the target result genes.
    """
    queryFH = open(outBaseFilename + '.query.txt', 'w')
    goldStdFH = open(outBaseFilename + '.goldStd.txt', 'w')
    groupFH = open(outBaseFilename + '.group.txt', 'w')

    print(query_pct)
    for group in groups:
        # determine the number of genes that will be used for each query
        group.queries = []
        for qpct in query_pct:
            query = StructDict()
            qnum = group.size * qpct / 100.0
            if qpct > 50:
                qnum = math.floor(qnum)
            else:
                qnum = math.ceil(qnum)
            query.qnum = qnum
            # create a random list of index values for the query genes
            query.q_indicies = random.sample(range(group.size), qnum)
            # create the inverse list for the results genes
            query.res_indicies = list(set(range(group.size)) - set(query.q_indicies))
            assert len(query.q_indicies) == query.qnum
            assert len(query.res_indicies) == group.size - query.qnum
            assert set(query.q_indicies).isdisjoint(set(query.res_indicies))
            assert len(group.genes) == group.size
            assert max(query.q_indicies) < group.size
            assert max(query.res_indicies) < group.size
            # select the query genes and result genes
            query.genes = [group.genes[i] for i in query.q_indicies]
            query.results = [group.genes[i] for i in query.res_indicies]
            # write the query genes to a file
            queryFH.write(",".join(query.genes) + "\n")
            # write the result genes to a file
            goldStdFH.write(",".join(query.results) + "\n")
            # write the group to a file
            groupFH.write("\t".join([group.id, group.desc]) + "\n")
            # groupFH.write("\t".join(group.genes) + "\n")
            group.queries.append(query)
        # end for query percents
    # end for groups
    queryFH.close()
    goldStdFH.close()
    groupFH.close()


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument('--min-gene-count', '-min', default="20", type=int,
                           help='min number of genes in a correlated group, default 20')
    argParser.add_argument('--max-gene-count', '-max', default="200", type=int,
                           help='max number of genes in a correlated group, default 200')
    argParser.add_argument('--query-pct', '-q', default=[], action='append',
                           help='percent of genes to keep as query, can specify multiple')
    argParser.add_argument('--input-file', '-i', type=str, required=True,
                           help='input file with list of correlated genes')
    argParser.add_argument('--output-file-base', '-o', type=str, required=True,
                           help='input file with list of correlated genes')
    args = argParser.parse_args()

    # Get the percentage of genes from a group to use for the query from the args
    query_pct = [int(y) for x in args.query_pct for y in x.split(',')]
    print("min genes {}, max genes {}, query_pct {}".
        format(args.min_gene_count, args.max_gene_count, query_pct))

    groups = parse_gmt(args.input_file, args.min_gene_count, args.max_gene_count)
    create_queries(groups, query_pct, args.output_file_base)
    # print(groups)