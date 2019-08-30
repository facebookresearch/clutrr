"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

# Clean the templates from mturk annotated data
# Input = mturk annotated file (amt_mturk.csv)
# Output = placeholder json

import pandas as pd
import argparse
from nltk.tokenize import word_tokenize
import difflib
import json
from sacremoses import MosesDetokenizer
detokenizer = MosesDetokenizer()


def extract_placeholder(df):
    """
    Given the AMT annotated datasets, extract the placeholders.
    Important to maintain the order of the entities after being matched
    For example, to replace a proof state (2,3),(3,4), the order is
    important.
    For the paper, we provide the set of cleaned train and test splits for the placeholders
    See `Clutrr.setup()` for download locations
    :param df:
    :return:
    """
    #skipped = [109] # skipping the Jose - Richard row, shouldn't have approved it
    skipped = []
    for i, row in df.iterrows():
        story = row['paraphrase']
        ents_gender = {dd.split(':')[0]: dd.split(':')[1] for dd in row['genders'].split(',')}
        words = word_tokenize(story)
        ent_id_g = {}
        if i in skipped:
            continue
        # skipping a problematic row where two names are very similar.
        # TODO: remove this from the AMT study as well
        if 'Micheal' in ents_gender and 'Michael' in ents_gender:
            skipped.append(i)
            continue
        # build entity -> key list
        # here order of entity is important, so first we fetch the ordering from
        # the proof state
        proof = eval(row['proof_state'])
        m_built = []
        if len(proof) > 0:
            built = []
            for prd in proof:
                pr_lhs = list(prd.keys())[0]
                pr_rhs = prd[pr_lhs]
                if pr_lhs not in built:
                    built.extend(pr_rhs)
                else:
                    pr_i = built.index(pr_lhs)
                    built[pr_i] = pr_rhs
            for b in built:
                if type(b) != list:
                    m_built.append(b)
                else:
                    m_built.extend(b)
        else:
            # when there is no proof state, consider the order from query
            query = eval(row['query'])
            m_built.append((query[0], '', query[-1]))
        # with the proof state, create an ordered ENT_id_gender dict
        ent_gender_keys = {}

        ordered_ents = []

        # add entities in the dictionary
        def add_ent(entity):
            if entity not in ent_gender_keys:
                ent_gender_keys[entity] = 'ENT_{}_{}'.format(len(ent_gender_keys), ents_gender[entity])
                ordered_ents.append(entity)

        for edge in m_built:
            add_ent(edge[0])
            add_ent(edge[-1])

        if len(ordered_ents) != len(ents_gender):
            print(i)
            return

        for ent_id, (ent, gender) in enumerate(ents_gender.items()):
            matches = difflib.get_close_matches(ent, words, cutoff=0.9)
            if len(matches) == 0:
                print(row['paraphrase'])
                print(ent)
                return
            match_idxs = [i for i, x in enumerate(words) if x in matches]
            for wi in match_idxs:
                words[wi] = ent_gender_keys[ent]
                ent_id_g[ent_id] = gender
        gender_key = '-'.join([ents_gender[ent] for ent in ordered_ents])
        replaced = detokenizer.detokenize(words, return_str=True)
        df.at[i, 'template'] = replaced
        df.at[i, 'template_gender'] = gender_key
    print('Skipped', skipped)
    return df, skipped

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mfile', type=str, default='amt_mturk.csv', help='MTurk generated file')
    parser.add_argument('--outfile', type=str, default='amt_placeholders', help='placeholders json file')
    parser.add_argument('--split', type=float, default=0.8, help='Train/Test split.')
    args = parser.parse_args()

    df = pd.read_csv(args.mfile)
    # do not use the rejected samples
    df = df[df.review != 'rejected']
    print("Number of accepted rows : {}".format(len(df)))
    df, skipped = extract_placeholder(df)
    # create a json file for easy lookup
    placeholders = {}
    for i, row in df.iterrows():
        if i in skipped:
            continue
        if row['f_comb'] not in placeholders:
            placeholders[row['f_comb']] = {}
        if row['template_gender'] not in placeholders[row['f_comb']]:
            placeholders[row['f_comb']][row['template_gender']] = []
        placeholders[row['f_comb']][row['template_gender']].append(row['template'])
    # training and testing split of the placeholders
    train_p = {}
    test_p = {}
    for key, gv in placeholders.items():
        if key not in train_p:
            train_p[key] = {}
            test_p[key] = {}
        for gk, ps in gv.items():
            split = int(len(placeholders[key][gk]) * args.split)
            train_p[key][gk] = placeholders[key][gk][:split]
            test_p[key][gk] = placeholders[key][gk][split:]
    # save
    json.dump(train_p, open(args.outfile + '.train.json','w'))
    json.dump(test_p, open(args.outfile + '.test.json', 'w'))
    json.dump(placeholders, open(args.outfile + '.json','w'))
    print("Done.")

if __name__ == '__main__':
    main()

