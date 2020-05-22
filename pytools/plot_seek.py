'''
Script to plot the Seek results to reproduce the graphs 1a and 1c in the Seek paper
'''
import os
import sys
import glob
import argparse
import matplotlib.pyplot as plt
sys.path.append(os.path.dirname(__file__))
from utils import file_appendline, file_read
from struct_dict import StructDict


filebase = "result_qgroup."

def plot_group(inputdir, outputdir, recall_pct):
    filecount = 0
    group = os.path.basename(inputdir)
    filepattern = os.path.join(inputdir, filebase + r'*')
    res = StructDict()
    for resultfile in glob.iglob(filepattern):
        # read in the results files per query size
        # get the query size from the end part of the file name
        qsize = os.path.basename(resultfile).split('.')[-1]
        qsize = int(qsize)
        lines = file_read(resultfile)
        # 1st line is min/max
        # 2nd line is 1st, 2nd, 3rd quartile
        quartiles = [float(x) for x in lines[1].split()]
        res[qsize] = quartiles
        filecount += 1

    # create an array of result values per query size
    qsizes = list(res.keys())
    qsizes.sort()
    print(qsizes)
    quartile_1 = [res[qsize][0] for qsize in qsizes]
    quartile_2 = [res[qsize][1] for qsize in qsizes]
    quartile_3 = [res[qsize][2] for qsize in qsizes]
    print(res)
    print(quartile_1)
    print(quartile_2)
    print(quartile_3)
    print("Dir {} processed {} files".format(group, filecount))

    # plot the array
    plt.plot(qsizes, quartile_1, color="gray")
    plt.plot(qsizes, quartile_2, color="black")
    plt.plot(qsizes, quartile_3, color="gray")
    plt.fill_between(qsizes, quartile_1, quartile_3, color="gray")
    plt.title('Processes {} genes'.format(group))
    plt.xlabel('Query size')
    plt.ylabel('Fold precision at {} over random'.format(recall_pct))
    # plt.draw()
    # plt.pause(1)
    outputfile = os.path.join(outputdir, '{}.pdf'.format(group))
    plt.savefig(outputfile)



if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument('--input-dir', '-i', type=str, required=True,
                           help='input directory where the SeekEvaluator results are')
    argParser.add_argument('--result-dir', '-o', type=str, required=True,
                           help='directory where result files will be written')
    argParser.add_argument('--recall-pct', '-p', type=str, required=True,
                           help='Recall depth percent as specified in the SeekMiner run')
    args = argParser.parse_args()

    plot_group(args.input_dir, args.result_dir, args.recall_pct)
