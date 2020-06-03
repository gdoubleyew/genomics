#!/bin/bash

source ~/.bashrc
if [ -z $CONDA_DEFAULT_ENV ] || [ $CONDA_DEFAULT_ENV != "genomics" ]; then
  conda activate genomics
fi

source ~/seek_env

# TODO - make a temp output directory for the results and update the config file


python test_seek_bioinform.py -c sample_test_config.toml


