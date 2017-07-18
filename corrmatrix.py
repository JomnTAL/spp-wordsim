#!/usr/bin/env python
# coding: utf8

import sys
import os
import logging
import argparse
import csv
import numpy as np
from scipy import stats, linalg
from pytools.loaders.embeddings import WordEmbeddings


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', help="Path to the CSV dataset")
    parser.add_argument('output', help="Path to the output file")
    parser.add_argument('embeddings', nargs='+',
                        help="Path to the embedding model")
    parser.add_argument('-w', '--wordset',
                        help="Path to a wordset used to filter the used embeddings")
    parser.add_argument('-l', '--logger', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help="Logging level: DEBUG, INFO (default), WARNING, ERROR")

    args = parser.parse_args()

    numeric_level = getattr(logging, args.logger.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: {}".format(args.logger))
    logging.basicConfig(level=numeric_level)

    return args


def cosine_similarity(vec1, vec2):
    return vec1.dot(vec2) / (linalg.norm(vec1) * linalg.norm(vec2))


def emb_correlation(dataset, word2vec1, word2vec2):
    pred1 = []
    pred2 = []
    common_words = set(word2vec1.keys()) & set(word2vec2.keys())
    for data in dataset:
        w1 = data[0].lower()
        w2 = data[1].lower()
        if w1 in common_words and w2 in common_words:
            pred1.append(cosine_similarity(word2vec1[w1], word2vec1[w2]))
            pred2.append(cosine_similarity(word2vec2[w1], word2vec2[w2]))

    return stats.stats.spearmanr(pred1, pred2)


def dump_matrix(output, matrix, embeddings):
    with open(output, 'w') as fout:
        writer = csv.writer(fout, lineterminator="\n")

        rows = []
        row = ["Embeddings"]
        row.extend([os.path.basename(filepath) for filepath in embeddings])
        rows.append(row)
        for i, emb1 in enumerate(embeddings):
            row = [emb1]
            for j, emb2 in enumerate(embeddings):
                row.append(matrix[i, j])
            rows.append(row)

        writer.writerows(rows)


def load_dataset(filename):
    header = {}
    dataset = []
    with open(filename, "r") as csv_in:
        csv_reader = csv.reader(csv_in)
        row = next(csv_reader)
        for idx, item in enumerate(row):
            header[item] = idx

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


def main():
    args = argparser()

    dataset, header = load_dataset(args.dataset)
    wordset = None
    if args.wordset is not None:
        wordset = load_wordset(args.wordset)

    word2vecs = {}
    for filepath in args.embeddings:
        word2vecs[filepath] = WordEmbeddings(filepath, wordset=wordset, lowercase=True).load()

    corr_matrix = np.zeros((len(args.embeddings), len(args.embeddings)))
    for i, emb1 in enumerate(args.embeddings):
        for j, emb2 in enumerate(args.embeddings):
            rho, p = emb_correlation(dataset, word2vecs[emb1], word2vecs[emb2])
            corr_matrix[i, j] = rho

    dump_matrix(args.output, corr_matrix, args.embeddings)


if __name__ == '__main__':
    main()
