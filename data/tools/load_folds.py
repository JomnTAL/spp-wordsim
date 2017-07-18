#!/usr/bin/env python

import argparse
import logging
import csv


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset')
    parser.add_argument('output')
    parser.add_argument('fold', nargs="+")
    parser.add_argument('-l', '--logger', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Logging level: DEBUG, INFO (default), WARNING, ERROR")
    args = parser.parse_args()

    numeric_level = getattr(logging, args.logger.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: {}".format(args.logger))
    logging.basicConfig(level=numeric_level)

    return args


def load_folds(folds):
    pairs = set()
    for fold in folds:
        with open(fold, 'r') as fin:
            csv_fold = csv.DictReader(fin)
            for line in csv_fold:
                pairs.add((line['prime'], line['target']))
    return pairs


def main():
    args = argparser()

    pairs = load_folds(args.fold)

    with open(args.dataset, 'r') as fin, open(args.output, 'w') as fout:
        csv_in = csv.DictReader(fin)

        print("target,prime,rt", file=fout)
        for line in csv_in:
            if (line['prime'], line['target']) not in pairs:
                continue
            print("{},{},{}".format(line['target'], line['prime'], line['rt']), file=fout)


if __name__ == '__main__':
    main()
