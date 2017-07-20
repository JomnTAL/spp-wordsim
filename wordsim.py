#!/usr/bin/env python
# coding: utf8

import os
import logging
import argparse
from scipy import linalg, stats
import csv
from prettytable import PrettyTable
from extramodules.embeddings import WordEmbeddings


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', help="Path to the CSV dataset")
    parser.add_argument('embeddings', nargs='+',
                        help="Path to the embedding model")
    parser.add_argument('-w', '--wordset',
                        help="Path to a wordset used to filter the used embeddings.")
    parser.add_argument('-o', '--output_csv',
                        help="Path to the output CSV file")
    parser.add_argument('-l', '--logger', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help="Logging level: DEBUG, INFO (default), WARNING, ERROR")

    args = parser.parse_args()

    numeric_level = getattr(logging, args.logger.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: {}".format(args.logger))
    logging.basicConfig(level=numeric_level)

    return args


def load_dataset(filename):
    header = {}
    dataset = []
    with open(filename, "r") as csv_in:
        csv_reader = csv.DictReader(csv_in)
        header = csv_reader.fieldnames

        for row in csv_reader:
            dataset.append(row)

    return dataset, header


def load_wordset(filename):
    wordset = set()
    with open(filename, "r") as fin:
        for line in fin:
            line = line.rstrip("\r\n")
            if not line:  # Don't add empty lines to the wordset
                continue
            wordset.add(line)

    return wordset


def cosine_similarity(vec1, vec2):
    return vec1.dot(vec2) / (linalg.norm(vec1) * linalg.norm(vec2))


def spearman_rho(vec1, vec2):
    return stats.stats.spearmanr(vec1, vec2)


def kendall_tau(vec1, vec2):
    return stats.stats.kendalltau(vec1, vec2)


def pearson(vec1, vec2):
    return stats.stats.pearsonr(vec1, vec2)


def evaluate(dataset, header, word2vec):
    pred, label = [], []
    found, notfound = 0, 0

    for data in dataset:
        w1 = data['prime'].lower()
        w2 = data['target'].lower()
        try:
            rt = float(data['rt'])
        except ValueError:
            notfound += 1
            continue
        if w1 in word2vec and w2 in word2vec:
            found += 1
            pred.append(cosine_similarity(word2vec[w1], word2vec[w2]))
            label.append(rt)
        else:
            notfound += 1

    rho, pr = spearman_rho(label, pred)
    tau, pt = kendall_tau(label, pred)

    result = (rho, pr, tau, pt, found, notfound)

    return result


def print_results(results):
    table = PrettyTable(["Embeddings", "rho", "rho p-value", "tau", "tau p-value", "Found", "Not Found"])
    table.align["Embeddings"] = "l"

    for key, value in results.items():
        table.add_row([key, value[0], value[1], value[2], value[3], value[4], value[5]])
    print(table)


def dump_results(output, results):
    with open(output, "w") as csv_out:
        writer = csv.writer(csv_out, lineterminator="\n")

        rows = []
        rows.append(["Embeddings", "rho", "rho p-value", "tau", "tau p-value", "Found", "Not Found"])
        for key, value in results.items():
            rows.append([key, value[0], value[1], value[2], value[3], value[4], value[5]])

        writer.writerows(rows)


def main():
    args = argparser()

    dataset, header = load_dataset(args.dataset)
    wordset = None
    if args.wordset is not None:
        wordset = load_wordset(args.wordset)

    # Loading all word embedding models
    word2vecs = {}
    for filename in args.embeddings:
        logging.info("Loading word embeddings from '{}'...".format(filename))
        word2vec = WordEmbeddings(filename, wordset=wordset).load()
        logging.info("Loaded {} word embeddings.".format(len(word2vec)))
        word2vecs[filename] = word2vec

    results = {}
    for filename in args.embeddings:
        word2vec = word2vecs[filename]
        basename = os.path.basename(filename)
        results[os.path.splitext(basename)[0]] = evaluate(dataset, header, word2vec)

    print_results(results)

    if args.output_csv is not None:
        dump_results(args.output_csv, results)


if __name__ == '__main__':
    main()
