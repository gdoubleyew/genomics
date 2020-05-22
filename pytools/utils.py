'''
Utility helper functions for common use by other scripts
'''


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
