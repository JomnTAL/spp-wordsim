#! /bin/bash

if [[ $# -ne 3 ]]; then
    echo "Usage: $0 full_dataset folds_directory output_basename" >&2
    exit 1
fi

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

dataset="$1"
folds="$2"
output="$3"

# P1: Dev/Test

python3 "$dir/load_folds.py" $dataset $output.dev_p1.csv $folds/fold_{0,1}.csv
python3 "$dir/load_folds.py" $dataset $output.test_p1.csv $folds/fold_{2,3,4,5,6,7,8,9}.csv


# P2: Dev/Test/Train

python3 "$dir/load_folds.py" $dataset $output.dev_p2.csv $folds/fold_{0,1}.csv
python3 "$dir/load_folds.py" $dataset $output.test_p2.csv $folds/fold_{2,3}.csv
python3 "$dir/load_folds.py" $dataset $output.train_p2.csv $folds/fold_{4,5,6,7,8,9}.csv
