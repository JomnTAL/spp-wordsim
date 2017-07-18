#! /bin/bash

if [ ! -d "data/ldt" ]; then
    mkdir data/ldt
fi

if [ ! -d "data/nt" ]; then
    mkdir data/nt
fi

python3 data/tools/create_datasets.py data/ldt/ldt_ data/ldt/ldt_data/raw/ldt/*.csv
python3 data/tools/create_datasets.py data/nt/nt_ data/nt/nt_data/raw/nt/*.csv

data/tools/create_splits.sh data/ldt/ldt_200ms.csv data/folds data/ldt/ldt_200ms
data/tools/create_splits.sh data/ldt/ldt_1200ms.csv data/folds data/ldt/ldt_1200ms
data/tools/create_splits.sh data/nt/nt_200ms.csv data/folds data/nt/nt_200ms
data/tools/create_splits.sh data/nt/nt_1200ms.csv data/folds data/nt/nt_1200ms
