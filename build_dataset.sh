#! /bin/bash

count_ldt=`ls -1 data/raw/ldt/*.csv 2>/dev/null | wc -l`
if [[ $count_ldt -lt 4 ]]; then
    echo "Error: You need to download the 4 LDT datasets from http://spp.montana.edu/ and put them in data/raw/ldt" >&2
    echo "       Read the README for more information." >&2
    exit 1
fi

count_nt=`ls -1 data/raw/nt/*.csv 2>/dev/null | wc -l`
if [[ $count_nt -lt 4 ]]; then
    echo "Error: You need to download the 4 NT datasets from http://spp.montana.edu/ and put them in data/raw/nt" >&2
    echo "       Read the README for more information." >&2
    exit 1
fi

if [[ ! -d "data/ldt" ]]; then
    mkdir data/ldt
fi

if [[ ! -d "data/nt" ]]; then
    mkdir data/nt
fi

if ! which python3 >/dev/null 2>&1 ; then
    echo "Error: Can't find python 3." >&2
    exit 1
fi

python3 data/tools/create_datasets.py data/ldt/ldt_ data/ldt/ldt_data/raw/ldt/*.csv
python3 data/tools/create_datasets.py data/nt/nt_ data/nt/nt_data/raw/nt/*.csv

data/tools/create_splits.sh data/ldt/ldt_200ms.csv data/folds data/ldt/ldt_200ms
data/tools/create_splits.sh data/ldt/ldt_1200ms.csv data/folds data/ldt/ldt_1200ms
data/tools/create_splits.sh data/nt/nt_200ms.csv data/folds data/nt/nt_200ms
data/tools/create_splits.sh data/nt/nt_1200ms.csv data/folds data/nt/nt_1200ms
