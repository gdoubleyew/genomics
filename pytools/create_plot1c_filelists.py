#!/usr/bin/python

'''
To reproduce the plot supplemental 1c from the Seek paper requires
grouping all query sizes together for all gene group sizes.
This program iterates through the output files from SeekMiner and groups them all
together making filelists to be used by SeekEvaluator.
The filelists expected by SeekEvaluator are query files, gscore files, goldStd files
include files, exclude files
'''

import os
import sys
import re
import glob
import argparse
#sys.path.append(os.path.dirname(__file__))
from utils import file_appendline, file_read


if __name__ == "__main__":
    # Iterate through a directory of query results (from SeekMiner)
    # Write out filelists (containing lists of filenames in the query groups)
    # The list files are for input to SeekEvaluator (query, gscore, goldStd, include, exclude)
    argParser = argparse.ArgumentParser()
    argParser.add_argument('--inputdir', '-i', type=str, required=True,
                           help='directories that contain the result files from SeekMiner')
    argParser.add_argument('--outputdir', '-o', type=str, required=True,
                           help='directory to write the filelists to')
    argParser.add_argument('--genefile', '-g', type=str, required=True,
                           help='list of all genes for the include file')
    args = argParser.parse_args()

    if not os.path.isabs(args.outputdir):
        args.outputdir = os.path.join(os.getcwd(), args.outputdir)

    queryfilelist = os.path.join(args.outputdir, 'filelist_seek1c.query')
    goldfilelist = os.path.join(args.outputdir, 'filelist_seek1c.gold')
    gscorefilelist = os.path.join(args.outputdir, 'filelist_seek1c.gscore')
    includefilelist = os.path.join(args.outputdir, 'filelist_seek1c.include')
    excludefilelist = os.path.join(args.outputdir, 'filelist_seek1c.exclude')

    queryfiles = []
    # inputDirs can be a list of directories
    inputDirs = args.inputdir.split(',')
    for dir in inputDirs:
        if not os.path.isabs(dir):
            dir = os.path.join(os.getcwd(), dir)
        filepattern = os.path.join(dir, r'[0-9]*.query')
        for queryfile in glob.iglob(filepattern):
            queryfiles.append(queryfile)

    filecount = 0
    for queryfile in queryfiles:
        filecount += 1
        # Add a line to each filelist
        file_appendline(queryfilelist, queryfile)
        file_appendline(goldfilelist, re.sub('query$', 'gold', queryfile))
        file_appendline(gscorefilelist, re.sub('query$', 'gscore', queryfile))
        file_appendline(includefilelist, args.genefile)
        file_appendline(excludefilelist, queryfile)

    assert filecount == len(queryfiles)
    if filecount == 0:
        print("No matching files found")
        exit(-1)

    print("Num files processed: {}".format(filecount))
