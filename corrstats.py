#! /usr/bin/env python

"""
Functions for calculating the statistical significant differences between two dependent or independent correlation
coefficients.
The Fisher and Steiger method is adopted from the R package http://personality-project.org/r/html/paired.r.html
and is described in detail in the book 'Statistical Methods for Psychology'
The Zou method is adopted from http://seriousstats.wordpress.com/2012/02/05/comparing-correlations/
Credit goes to the authors of above mentioned packages!

Author: Philipp Singer (www.philippsinger.info)
"""

from __future__ import division
from __future__ import print_function

import numpy as np
from scipy.stats import t, norm
# from scipy.optimize import minimize
from math import atanh, pow
from numpy import tanh
import logging
import argparse
import os
import sys
import csv


__author__ = 'psinger'


def rz_ci(r, n, conf_level=0.95):
    zr_se = pow(1 / (n - 3), .5)
    moe = norm.ppf(1 - (1 - conf_level) / float(2)) * zr_se
    zu = atanh(r) + moe
    zl = atanh(r) - moe
    return tanh((zl, zu))


def rho_rxy_rxz(rxy, rxz, ryz):
    num = (ryz - 1 / 2. * rxy * rxz) * (1 - pow(rxy, 2) - pow(rxz, 2) - pow(
        ryz, 2)) + pow(ryz, 3)
    den = (1 - pow(rxy, 2)) * (1 - pow(rxz, 2))
    return num / float(den)


def dependent_corr(xy,
                   xz,
                   yz,
                   n,
                   twotailed=True,
                   conf_level=0.95,
                   method='steiger'):
    """
    Calculates the statistic significance between two dependent correlation coefficients
    @param xy: correlation coefficient between x and y
    @param xz: correlation coefficient between x and z
    @param yz: correlation coefficient between y and z
    @param n: number of elements in x, y and z
    @param twotailed: whether to calculate a one or two tailed test, only works for 'steiger' method
    @param conf_level: confidence level, only works for 'zou' method
    @param method: defines the method uses, 'steiger' or 'zou'
    @return: t and p-val
    """
    if method == 'steiger':
        d = xy - xz
        determin = 1 - xy ** 2 - xz ** 2 - yz ** 2 + 2 * xy * xz * yz
        av = (xy + xz) / 2
        cube = (1 - yz) * (1 - yz) * (1 - yz)

        t2 = d * np.sqrt((n - 1) * (1 + yz) / ((
            (2 * (n - 1) / (n - 3)) * determin + av * av * cube)))
        p = 1 - t.cdf(abs(t2), n - 3)

        if twotailed:
            p *= 2

        return t2, p
    elif method == 'zou':
        L1 = rz_ci(xy, n, conf_level=conf_level)[0]
        U1 = rz_ci(xy, n, conf_level=conf_level)[1]
        L2 = rz_ci(xz, n, conf_level=conf_level)[0]
        U2 = rz_ci(xz, n, conf_level=conf_level)[1]
        rho_r12_r13 = rho_rxy_rxz(xy, xz, yz)
        lower = xy - xz - pow((pow((xy - L1), 2) + pow(
            (U2 - xz), 2) - 2 * rho_r12_r13 * (xy - L1) * (U2 - xz)), 0.5)
        upper = xy - xz + pow((pow((U1 - xy), 2) + pow(
            (xz - L2), 2) - 2 * rho_r12_r13 * (U1 - xy) * (xz - L2)), 0.5)
        return lower, upper
    else:
        raise Exception('Wrong method!')


def independent_corr(xy,
                     ab,
                     n,
                     n2=None,
                     twotailed=True,
                     conf_level=0.95,
                     method='fisher'):
    """
    Calculates the statistic significance between two independent correlation coefficients
    @param xy: correlation coefficient between x and y
    @param xz: correlation coefficient between a and b
    @param n: number of elements in xy
    @param n2: number of elements in ab (if distinct from n)
    @param twotailed: whether to calculate a one or two tailed test, only works for 'fisher' method
    @param conf_level: confidence level, only works for 'zou' method
    @param method: defines the method uses, 'fisher' or 'zou'
    @return: z and p-val
    """

    if method == 'fisher':
        xy_z = 0.5 * np.log((1 + xy) / (1 - xy))
        ab_z = 0.5 * np.log((1 + ab) / (1 - ab))
        if n2 is None:
            n2 = n

        se_diff_r = np.sqrt(1 / (n - 3) + 1 / (n2 - 3))
        diff = xy_z - ab_z
        z = abs(diff / se_diff_r)
        p = (1 - norm.cdf(z))
        if twotailed:
            p *= 2

        return z, p
    elif method == 'zou':
        L1 = rz_ci(xy, n, conf_level=conf_level)[0]
        U1 = rz_ci(xy, n, conf_level=conf_level)[1]
        L2 = rz_ci(ab, n2, conf_level=conf_level)[0]
        U2 = rz_ci(ab, n2, conf_level=conf_level)[1]
        lower = xy - ab - pow((pow((xy - L1), 2) + pow((U2 - ab), 2)), 0.5)
        upper = xy - ab + pow((pow((U1 - xy), 2) + pow((ab - L2), 2)), 0.5)
        return lower, upper
    else:
        raise Exception('Wrong method!')


# print(dependent_corr(0.9, 1, .5, 30, method='steiger'))
# print independent_corr(0.5, 0.6, 103, 103, method='fisher')


# def stest_p(xt, yt, xy, n_elts, p0):
#     t, pval = dependent_corr(xt, yt, xy, n_elts, method='steiger')
#     if t is None:
#         return False
#     if pval < p0:
#         return True
#     return False


def load_corr_matrix(filename):
    embeddings_models = {}
    corr_matrix = None

    with open(filename, "r") as csv_in:
        csv_reader = csv.reader(csv_in)
        row = next(csv_reader)
        for idx, model_name in enumerate(row[1:]):
            model_name = os.path.splitext(os.path.basename(model_name))[0]
            embeddings_models[model_name] = idx

        corr_matrix = np.zeros((len(embeddings_models), len(embeddings_models)))

        for i, row in enumerate(csv_reader):
            for j, value in enumerate(row[1:]):
                corr_matrix[i, j] = float(value)

    return corr_matrix, embeddings_models


def load_corr_gold(filename, ref_model):
    ref = None
    others = {}
    with open(filename, "r") as csv_in:
        csv_reader = csv.reader(csv_in)
        next(csv_reader)  # We don't need to save the content of the header
        for row in csv_reader:
            if row[0] == ref_model:
                ref = float(row[1])
                continue
            others[row[0]] = float(row[1])

    return ref, others


def dump_results(results, ref_model):
    rows = []
    csv_writer = csv.writer(sys.stdout, lineterminator="\n")

    row = [""]
    for other in results:
        row.append(other)
    rows.append(row)

    row = [ref_model]
    for other in results:
        row.append(results[other])
    rows.append(row)

    csv_writer.writerows(rows)


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('ref_model',
                        help="Name of the word embeddings model to use as reference")
    parser.add_argument('corr_dataset',
                        help="Path to the file which contains the correlations between word embedding models and the dataset (CSV output from wordsim.py)")
    parser.add_argument('corr_matrix',
                        help="Path to the CSV file obtained with corrmatrix.py")
    parser.add_argument('n_elements', type=int,
                        help="The number of pairs of words that were used to calculate the correlations.")
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
    corr_mat, embeddings = load_corr_matrix(args.corr_matrix)
    ref, others = load_corr_gold(args.corr_gold, args.ref_model)

    results = {}
    for other in others:
        ref_idx = embeddings[args.ref_model]
        other_idx = embeddings[other]
        print(ref, others[other], corr_mat[ref_idx, other_idx])
        t2, pval = dependent_corr(ref, others[other], corr_mat[ref_idx, other_idx], args.n_elements)
        results[other] = pval

    dump_results(results, args.ref_model)


if __name__ == '__main__':
    main()
