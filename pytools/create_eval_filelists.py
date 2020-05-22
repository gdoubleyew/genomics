#!/usr/bin/python

'''
To reproduce the plots from the Seek paper, supplemental 1a and 1c, requires
grouping queries by query size (such as all queries with 2 genes, and all with 4 genes etc).
This program iterates through the output files from SeekMiner and groups them by
query size and creates a set of filelists for each query size to be used by SeekEvaluator.
The filelists expected by SeekEvaluator are query files, gscore files, goldStd files
include files, exclude files
'''

import os
import sys
import glob
import argparse
sys.path.append(os.path.dirname(__file__))
from utils import file_appendline, file_read


if __name__ == "__main__":
    # Iterate through a directory of query results (from SeekMiner)
    # Group queries by size (number of genes per query)
    # Write out list files (containing lists of filenames in the query groups)
    # The list files are for input to SeekEvaluator (query, gscore, goldStd, include, exclude)
    argParser = argparse.ArgumentParser()
    argParser.add_argument('--inputdir', '-i', type=str, required=True,
                           help='directory that contains the result files from SeekMiner')
    argParser.add_argument('--outputdir', '-o', type=str, required=True,
                           help='directory to write the filelists to')
    argParser.add_argument('--genefile', '-g', type=str, required=True,
                           help='list of all genes for the include file')
    args = argParser.parse_args()

    if not os.path.isabs(args.inputdir):
        args.inputdir = os.path.join(os.getcwd(), args.inputdir)

    # filelists to create
    filelists = ['query', 'gscore', 'gold']

    filepattern = os.path.join(args.inputdir, r'[0-9]*.query')
    filecount = 0
    for queryfile in glob.iglob(filepattern):
        filecount += 1
        # print(queryfile)
        # read file to find query size
        lines = file_read(queryfile)
        assert len(lines) == 1
        num_genes = len(lines[0].split())
        path, base = os.path.split(queryfile)
        # append the files to the appropriate lists
        for name in filelists:
            listname = os.path.join(args.outputdir, 'filelist_q{}.{}'.format(num_genes, name))
            # substitue name for 'query' in the queryfilename
            newbase = base.replace('query', name)
            lfile = os.path.join(path, newbase)
            file_appendline(listname, lfile)
        # Add a line to the include and exclude file
        # include all genes given in gene file
        includefile = os.path.join(args.outputdir, 'filelist_q{}.include'.format(num_genes))
        file_appendline(includefile, args.genefile)
        # exclude all genes in the query file
        excludefile = os.path.join(args.outputdir, 'filelist_q{}.exclude'.format(num_genes))
        file_appendline(excludefile, queryfile)

    if filecount == 0:
        print("No matching files found")
        exit(-1)

    print("Num files processed: {}".format(filecount))
