'''
Given two files with ranked lists of genes or datasets, determine how closely the
rankings of the files agree using Spearmans correlation.
FileA and FileB can have multiple lines, each line will be correlated with the
corresponding line in the other file and a list of correlation values will be
returned with one value per line.
Note that FileB is compared against FileA. So FileA ranking is the standard
and for each value in FileA a rank is looked up in FileB. If the value doesn't
appear in FileB then the rank will be 0 for B.
'''
import scipy.stats as stats
import utils


def files_rank_correlation(fileA, fileB):
    # read in the file data lines
    A_lines = utils.file_read(fileA)
    B_lines = utils.file_read(fileB)

    assert len(A_lines) == len(B_lines)

    correlations = []
    # for each line calculate the correlation between the two files
    for i in range(len(A_lines)):
        # assign an order rank to the values in the line
        A_dict_rank = {val: j for j, val in enumerate(A_lines[i].split())}
        B_dict_rank = {val: j for j, val in enumerate(B_lines[i].split())}
        A_rank = []
        B_rank = []
        # for each value in line A get the rank order in list A and B
        keys = list(A_dict_rank.keys())
        max_rank = len(keys)
        for key in keys:
            A_rank.append(A_dict_rank[key])
            B_rank.append(B_dict_rank.get(key, max_rank))
        # calculate the spearman's correlation coefficient between the two rankings
        corr, _ = stats.spearmanr(A_rank, B_rank)
        print(A_rank)
        print(B_rank)
        correlations.append(corr)

    return correlations


if __name__ == "__main__":
    fileA = '/Users/gwallace/tmp/1_0.results.txt'
    fileB = '/Users/gwallace/tmp/2_0.results.txt'

    corr = files_rank_correlation(fileA, fileB)
    print(corr)
