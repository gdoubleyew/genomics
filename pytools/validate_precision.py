"""
Script to verify that the precision calculated by eval_precision.py (using SeekEvaluator)
match the expected result based on the result gene list and gold standard list.
Example:
python cmp_res_gold.py -r /tmp/res/outshort/10.gene_result.txt \
    -g /tmp/res/outshort/10.gold -a eval_precision_out.txt -i 10

Previous name: cmp_res_gold.py
"""

import sys
import argparse


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument('--single-res-file', '-r', type=str, required=True,
                           help='gene score as text file for one query')
    argParser.add_argument('--single-gold-file', '-g', type=str, required=True,
                           help='gold standard file for one queries')
    argParser.add_argument('--group-res-file', '-a', type=str, required=True,
                           help='result file from a test run (i.e. precision at '
                           'each recall dept for each query in the group')
    argParser.add_argument('--query-index', '-i', type=int, required=True,
                           help='index of the query within the query group')
    args = argParser.parse_args()

    with open(args.single_gold_file, 'r') as fp:
        goldlines = fp.readlines()

    with open(args.single_res_file, 'r') as fp:
        reslines = fp.readlines()

    with open(args.group_res_file, 'r') as fp:
        grouplines = fp.readlines()

    assert len(goldlines) == 1
    goldvals = goldlines[0].split()

    resvals = []
    for l in reslines:
        v = l.split()
        resvals.append(v[0])

    # print(goldvals)
    # print(resvals)

    # for each gold val, find out the index position in the resvals
    idxvals = []
    num_not_found = 0
    for g in goldvals:
        try:
            idx = resvals.index(g)
        except ValueError:
            num_not_found += 1
            print("missing {}".format(g))
        idxvals.append(idx)

    # check one
    checkidx = int(len(idxvals)/2)
    assert resvals[idxvals[checkidx]] == goldvals[checkidx]

    # then sort the gold val index positions
    idxvals.sort()
    print(idxvals)

    # then calculate the precision at each sorted gold val
    precisionVals = []
    matches = 0
    for i in idxvals:
        matches += 1
        precision = matches / (i+1)
        precisionVals.append(round(precision, 5))
        print("precision: {:.6f}".format(precision))

    print("missing results {}".format(num_not_found))

    # compare our precision to one created by the test framework
    extPrecision = [float(x) for x in grouplines[args.query_index].split()]
    for i in range(len(precisionVals)):
        print("{}: {}-{}: diff {}".format(i, precisionVals[i], extPrecision[i], precisionVals[i]-extPrecision[i]))
    print("lenghts: {}, {}".format(len(precisionVals), len(extPrecision)))
