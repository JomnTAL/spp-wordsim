#!/usr/bin/env python

import os
import argparse
import logging
import csv
from scipy import stats


def load_other_dataset(filepath):
    dataset = {}
    with open(filepath, 'r') as fin:
        for line in fin:
            line = line.rstrip('\r\n')
            tokens = line.split('\t')
            word1 = tokens[0].lower()
            word2 = tokens[1].lower()
            score = float(tokens[2])
            if (word1, word2) not in dataset:
                dataset[(word1, word2)] = score
                dataset[(word2, word1)] = score

    return dataset


def load_spp_dataset(filepath):
    dataset = {}
    with open(filepath, "r") as csv_in:
        csv_reader = csv.DictReader(csv_in)

        for row in csv_reader:
            prime = row['prime'].lower()
            target = row['target'].lower()
            if not row['rt']:
                continue
            score = float(row['rt'])
            if (prime, target) not in dataset:
                dataset[(prime, target)] = score

    return dataset


def spearman_rho(vec1, vec2):
    return stats.stats.spearmanr(vec1, vec2)


def correlation(spp_dataset, other_dataset, common_pairs):
    spp_scores = []
    other_scores = []

    for pair in common_pairs:
        spp_scores.append(spp_dataset[pair])
        other_scores.append(other_dataset[pair])
        print("{} - {} {}".format(pair, spp_dataset[pair], other_dataset[pair]))

    rho, pr = spearman_rho(spp_scores, other_scores)

    return rho


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('spp_dataset',
                        help="Path to a SPP dataset (CSV format)")
    parser.add_argument('other_dataset', nargs='+',
                        help="Paths to other datasets (TSV format with no header)")
    parser.add_argument('-l', '--logger', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Logging level: DEBUG, INFO (default), WARNING, ERROR")
    args = parser.parse_args()

    numeric_level = getattr(logging, args.logger.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: {}".format(args.logger))
    logging.basicConfig(level=numeric_level)

    return args


def main():
    args = argparser()

    spp_dataset = load_spp_dataset(args.spp_dataset)

    print("dataset,rho,n_common")
    for other_dataset_name in args.other_dataset:
        other_dataset = load_other_dataset(other_dataset_name)
        common_pairs = spp_dataset.keys() & other_dataset.keys()

        rho = correlation(spp_dataset, other_dataset, common_pairs)

        name = os.path.splitext(os.path.basename(other_dataset_name))[0]
        print("{},{},{}".format(name, rho, len(common_pairs)))


if __name__ == '__main__':
    main()
