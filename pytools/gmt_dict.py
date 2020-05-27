'''
Given a GO gmt file and a list of GO descriptions, pull out the gmt groups from the list
from the gmt file and write those to a new file.
'''

import sys
import argparse
from utils import parse_gmt, file_read


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument('--gmt-file', '-g', type=str, required=True,
                           help='input file with list of correlated genes')
    argParser.add_argument('--group-list', '-l', type=str, required=True,
                           help='list of GO groups to pull out')
    argParser.add_argument('--output-file', '-o', type=str, required=True,
                           help='output file of matching groups')
    args = argParser.parse_args()

    glist = file_read(args.group_list)

    gmt = parse_gmt(args.gmt_file, 0, sys.maxsize)

    gmt_dict = {}
    for group in gmt:
        gmt_dict[group['desc']] = group

    with open(args.output_file, 'w') as fp:
        count = 0
        for desc in glist:
            desc = desc.rstrip()
            group = gmt_dict.get(desc, None)
            if group is not None:
                fp.write(group['line'])
                count += 1

    print("wrote {} groups".format(count))

    # print(gmt)
