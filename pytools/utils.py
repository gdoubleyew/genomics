'''
Utility helper functions for common use by other scripts
'''
import os
import re
from struct_dict import StructDict


def file_read(filename):
    with open(filename, 'r') as fp:
        lines = fp.readlines()
    return lines


def file_appendline(filename, data):
    with open(filename, 'a') as fp:
        fp.write(data+'\n')


def read_genes(gene_file):
    '''
    Read in file with sets of genes, one set per line.
    Return a list of lists containing the gene sets.
    '''
    groups = []
    with open(gene_file, 'r') as fp:
        for line in fp:
            line = line.rstrip("\n")
            groups.append(line)
    return groups


def write_goldstd(goldstd, outdir):
    '''
    Take as input a file with a list of gold standard genes one per line
    corresponding to the query genes one per line in a query file. Convert
    this to a set of files numbered 0 to numlines where each output file
    has one line worth of gold standard genes corresponding to one query.
    '''
    for i, g in enumerate(goldstd):
        fw = open("%s/%d.gold" % (outdir, i), "w")
        fw.write(g + "\n")
        fw.close()


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
            mtch = re.search(r'(.*)\((\d+)\)', desc)
            if mtch is None:
                raise ValueError("Description missing gene count, {}".format(desc))
            num_genes = int(mtch.group(2))
            desc = mtch.group(1).rstrip()
            assert len(genes) == num_genes
            if num_genes >= min_gene_count and num_genes <= max_gene_count:
                group = StructDict({'id': group_id, 'desc': desc, 'genes': genes, 'size': num_genes, 'line': line})
                groups.append(group)
    return groups
