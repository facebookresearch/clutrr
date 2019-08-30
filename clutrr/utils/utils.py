"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

import itertools as it
import numpy as np
import csv
import pandas as pd
import random


def pairwise(iterable):
    """
    Recipe from itertools
    :param iterable:
    :return: "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    """
    a, b = it.tee(iterable)
    next(b, None)
    return zip(a, b)

def prob_dist(rows):
    row_dict = {}
    for row in rows:
        if row[-1] not in row_dict:
            row_dict[row[-1]] = []
        row_dict[row[-1]].append(row[:2])
    rel_probs = {k: (len(v) / len(rows)) for k, v in row_dict.items()}
    return rel_probs

def split_train_test(args, rows):
    # split training testing
    r1 = prob_dist(rows)
    indices = range(len(rows))
    mask_i = np.random.choice(indices,
                              int(len(indices) * args.train_test_split),
                              replace=False)
    test_indices = [i for i in indices if i not in set(mask_i)]
    train_indices = [i for i in indices if i in set(mask_i)]
    train_rows = [rows[ti] for ti in train_indices]
    r_train = prob_dist(train_rows)
    test_rows = [rows[ti] for ti in test_indices]
    r_test = prob_dist(test_rows)
    train_rows = [row[:-1] for row in train_rows]
    test_rows = [row[:-1] for row in test_rows]

    return train_rows, test_rows

def write2file(args, rows, filename):
    with open(filename, 'w') as fp:
        for argi in vars(args):
            fp.write('# {} {}\n'.format(argi, getattr(args, argi)))
        writer = csv.writer(fp)
        writer.writerow(['story','summary'])
        for row in rows:
            writer.writerow(row)

def sanity_check(filename, rows):
    ## sanity check
    df = pd.read_csv(filename, skip_blank_lines=True, comment='#')
    print('Total rows : {}'.format(len(df)))
    assert len(rows) == len(df)


class CDS:
    def combinationSum(self, candidates, target):
        res = []
        candidates.sort()
        self.dfs(candidates, target, 0, [], res)
        return res

    def dfs(self, nums, target, index, path, res):
        if target < 0:
            return  # backtracking
        if target == 0:
            res.append(path)
            return
        for i in range(index, len(nums)):
            self.dfs(nums, target - nums[i], i, path + [nums[i]], res)


class unique_element:
    def __init__(self, value, occurrences):
        self.value = value
        self.occurrences = occurrences


def perm_unique(elements):
    eset = set(elements)
    listunique = [unique_element(i, elements.count(i)) for i in eset]
    u = len(elements)
    return perm_unique_helper(listunique, [0] * u, u - 1)


def perm_unique_helper(listunique, result_list, d):
    if d < 0:
        yield tuple(result_list)
    else:
        for i in listunique:
            if i.occurrences > 0:
                result_list[d] = i.value
                i.occurrences -= 1
                for g in perm_unique_helper(listunique, result_list, d - 1):
                    yield g
                i.occurrences += 1


def comb_indexes(sn, max_seq_len=3):
    """
    Idea here is to generate all combinations maintaining the order
    Eg, [a,b,c,d] => [[a],[b],[c],[d]], [[a,b],[c],[d]], [[a,b,c],[d]], etc ...
    where the max sequence is max_seq_len
    :param sn:
    :param max_seq_len:
    :return:
    """
    s_n = len(sn)
    cd = CDS()
    some_comb = cd.combinationSum(list(range(1,max_seq_len+1)),s_n)
    all_comb = [list(perm_unique(x)) for x in some_comb]
    all_comb = [y for r in all_comb for y in r]
    pairs = []
    for pt in all_comb:
        rsa = []
        stt = 0
        for yt in pt:
            rsa.append(sn[stt:stt+yt])
            stt += yt
        pairs.append(rsa)
    return pairs

def choose_random_subsequence(sn, max_seq_len=3):
    return random.choice(comb_indexes(sn, max_seq_len))