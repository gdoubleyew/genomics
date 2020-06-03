import os
import time
import argparse

# parameters to test
# "-V" ["CV","EQUAL","ORDER_STAT","VAR","USER","AVERAGE_Z","CV_CUSTOM"]
# "-I" ["LOI","LOO","XFOLD"] # for CV mode
# "-z" ["pearson","z_score"]
# "-e" # for z_score method
# "-m"
# "-M"
# "-S"
# "-C" 1
param_tests = {
    "test1": "",
    "test2": "-m M",
    "test3": "-V CV -I LOI",
    "test4": "-V CV -I LOO",
    "test5": "-V CV -I XFOLD",
    "test6": "-V EQUAL",
    "test7": "-V ORDER_STAT",
    "test8": "-V VAR",
    "test9": "-V USER",
    "test10": "-V AVERAGE_Z",
    "test11": "-V CV_CUSTOM",
    "test12": "-z pearson",
    "test13": "-z z_score",
    "test14": "-z z_score -e",
    "test15": "-S",
    "test16": "-C 1.0",
}


def mktempdir():
    timestamp = str(int(time.time()))
    temp_dir = "/tmp/param_test_" + timestamp
    os.mkdir(temp_dir)
    return temp_dir


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument('--seekdir', '-s', type=str, required=True,
                           help='Seek directory')
    argParser.add_argument('--query_file', '-q', type=str, required=True,
                           help='query file to be used')
    args = argParser.parse_args()

    tmpdir = mktempdir()
    os.chdir(args.seekdir)
    # print(param_tests)
    for test, params in param_tests.items():
        print("{}, {}".format(test, params))
        resultdir = os.path.join(tmpdir, test)
        os.mkdir(resultdir)
        cmd = "source ./seek_env; " \
              "./bin/SeekMiner -x dataset.map -i gene_map.txt " \
              "-d db.combined -p prep.combined -P platform.combined -Q quant2 " \
              "-u sinfo.combined -R dataset_size -n 1000 -b 200 " \
              "-q {queryfile} -o {resultdir} -O {params}". \
              format(resultdir=resultdir, queryfile=args.query_file, params=params)
        # print(cmd)
        os.system(cmd)

        # TODO compare output to gold standard results
