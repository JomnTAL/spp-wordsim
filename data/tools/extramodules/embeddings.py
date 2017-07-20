# coding: utf-8
"""
Module that allows to easily load embeddings.
"""

import os
import logging
import gzip
import numpy as np
import tqdm


class WordEmbeddings:
    """ Class that allows you to iterate through the word embeddings in a file.
    The input file can be gzipped.

    Args: 
      filepath (str): Path to the file with word embeddings
      wordset (set): Set of words to use as a filter. Only words that are in this set will be loaded.
    """
    def __init__(self, filepath, wordset=None, lowercase=False):
        self.filepath = filepath
        self.wordset = wordset
        self._n_embeddings = None
        self.lowercase = lowercase
        if filepath.endswith(".gz"):
            fin = gzip.open(filepath, 'rt')
        else:
            fin = open(filepath, 'r')

        line = fin.readline().rstrip(" \r\n")
        tokens = line.split(' ')
        if len(tokens) == 2:  # W2V format
            self.dim = int(tokens[1])
            self._n_embeddings = int(tokens[0])
        else:                 # GloVe format
            self.dim = len(tokens) - 1

        fin.close()

    def __iter__(self):
        line_nb = 0
        if self.filepath.endswith(".gz"):
            fin = gzip.open(self.filepath, 'rt')
        else:
            fin = open(self.filepath, 'r')
        with tqdm.tqdm(total=self._n_embeddings,
                       desc="Loading '{}' progress".format(self.filepath),
                       unit=" words") as pbar:
            for line in fin:
                line_nb += 1
                line = line.rstrip(" \r\n")
                tokens = line.split(' ')
                if len(tokens) == 2:  # W2V format
                    continue
                pbar.update(1)
                if self.dim != len(tokens) - 1:
                    basename = os.path.basename(self.filepath)
                    logging.warning("[%s:%d] Embedding dimension error (%d vs %d) ! Skipping...",
                                    basename, line_nb, len(tokens) - 1, self.dim)
                    continue
                word = tokens[0]
                if self.lowercase:
                    word = word.lower()
                if self.wordset is not None and word not in self.wordset:
                    continue
                coefs = np.asarray(tokens[1:], dtype='float32')
                yield word, coefs

        fin.close()

    def load(self):
        """ Loads the entire embedding file into a dictionary """
        embeddings = {}
        for word, coefs in self:
            embeddings[word] = coefs
        return embeddings

    def load_words(self):
        """ Only load the words in the embedding file """
        words = set()
        for word, coefs in self:
            words.add(word)
        return words


class SentenceEmbeddings:
    """ Class that allows you to iterate through the sentence embeddings in a file.
    The input file can be gzipped.

    Args: 
      filepath (str): Path to the file with word embeddings
    """
    def __init__(self, filepath, lowercase=False):
        self.filepath = filepath
        self.lowercase = lowercase

    def __iter__(self):
        if self.filepath.endswith(".gz"):
            fin = gzip.open(self.filepath, 'rt')
        else:
            fin = open(self.filepath, 'r')
        for line in fin:
            line = line.rstrip(" \r\n")
            tokens = line.split('\t')
            sentence = tokens[0]
            vector = tokens[1]
            vector_tokens = vector.split(' ')
            if self.lowercase:
                sentence = sentence.lower()
            coefs = np.asarray(vector_tokens, dtype='float32')
            yield sentence, coefs

        fin.close()

    def load(self):
        """ Loads the entire embedding file into a dictionary """
        embeddings = {}
        for sentences, coefs in self:
            embeddings[sentences] = coefs
        return embeddings

    def load_sentences(self):
        """ Only load the sentences in the embedding file """
        sentences = set()
        for sentence, coefs in self:
            sentences.add(sentence)
        return sentences
