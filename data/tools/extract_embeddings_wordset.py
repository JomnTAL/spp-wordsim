#!/usr/bin/env python
# coding: utf8

import argparse
import logging
from extramodules.embeddings import WordEmbeddings


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('embeddings', nargs="+",
                        help="Path to the embedding model")
    parser.add_argument('-o', '--output',
                        help="Path to the output file")
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
    intersect = None
    for model_filename in args.embeddings:
        # print("Loading '{}'...".format(model_filename), file=sys.stderr)
        wordset = WordEmbeddings(model_filename, lowercase=True).load_words()
        if intersect is not None:
            intersect &= wordset
        else:
            intersect = wordset

    if args.output is None:
        print(*intersect, sep="\n")
    else:
        with open(args.output, "w") as fout:
            print(*intersect, sep="\n", file=fout)


if __name__ == '__main__':
    main()
