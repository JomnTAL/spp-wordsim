#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
import csv


def load_freqs(filepath, word_column):
    freqs = {}

    with open(filepath, 'r') as fin:
        csv_in = csv.DictReader(fin)

        for row in csv_in:
            if row['SubFreq']:
                freqs[row[word_column]] = float(row['SubFreq'])

    return freqs


def calculate_mean_freq(filepath, target_freqs, prime_freqs):
    with open(filepath, 'r') as fin:
        csv_in = csv.DictReader(fin)

        total_freq = 0
        n_pairs = 0
        for row in csv_in:
            target = row['target']
            prime = row['prime']

            if target not in target_freqs or prime not in prime_freqs:
                continue

            n_pairs += 1
            total_freq += target_freqs[target] + prime_freqs[prime]

    return total_freq / n_pairs


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('target_freqs')
    parser.add_argument('prime_freqs')
    parser.add_argument('dataset', nargs='+')
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

    target_freqs = load_freqs(args.target_freqs, "TargetWord")
    prime_freqs = load_freqs(args.prime_freqs, "Prime")

    for dataset in args.dataset:
        mean_freq = calculate_mean_freq(dataset, target_freqs, prime_freqs)
        print("{}: {}".format(dataset, mean_freq))


if __name__ == '__main__':
    main()
