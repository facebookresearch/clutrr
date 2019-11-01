"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

# Generate story-summary pairs

from clutrr.actors.ancestry import Ancestry
from clutrr.relations.builder import RelationBuilder
from tqdm import tqdm
import random
import numpy as np
import json
import copy

from clutrr.args import get_args
from clutrr.store.store import Store
from clutrr.utils.utils import comb_indexes
import pandas as pd
from clutrr.relations.templator import *

#store = Store()

def generate_rows(args, store, task_name, split=0.8, prev_patterns=None):
    # pre-flight checks
    combination_length = min(args.combination_length, args.relation_length)
    if not args.use_mturk_template:
        if combination_length > 1:
            raise NotImplementedError("combination of two or more relations not implemented in Synthetic templating")
    else:
        if combination_length > 3:
            raise NotImplementedError("combinations of > 3 not implemented in AMT Templating")
    # generate
    print(args.relation_length)
    print("Loading templates...")
    all_puzzles = {}
    if args.template_split:
        train_templates = json.load(open(args.template_file + '.train.json'))
        test_templates = json.load(open(args.template_file + '.test.json'))
    else:
        train_templates = json.load(open(args.template_file + '.json'))
        test_templates = json.load(open(args.template_file + '.json'))
    if args.use_mturk_template:
        templatorClass = TemplatorAMT
    else:
        synthetic_templates_per_rel = {}
        for key, val in store.relations_store.items():
            for gender, gv in val.items():
                synthetic_templates_per_rel[gv['rel']] = gv['p']
        templatorClass = TemplatorSynthetic
        train_templates = synthetic_templates_per_rel
        test_templates = synthetic_templates_per_rel
    pb = tqdm(total=args.num_rows)
    num_stories = args.num_rows
    stories_left = num_stories
    columns = ['id', 'story', 'query', 'text_query', 'target', 'text_target', 'clean_story', 'proof_state', 'f_comb',
               'task_name','story_edges','edge_types','query_edge','genders', 'syn_story', 'node_mapping', 'task_split']
    f_comb_count = {}
    rows = []
    anc_num = 0
    anc_num += 1
    anc = Ancestry(args, store)
    rb = RelationBuilder(args, store, anc)
    while stories_left > 0:
        status = rb.build()
        if not status:
            rb.reset_puzzle()
            rb.anc.next_flip()
            continue
        rb.add_facts()
        # keeping a count of generated patterns to make sure we have homogenous distribution
        if len(f_comb_count) > 0 and args.equal:
            min_c = min([v for k,v in f_comb_count.items()])
            weight = {k:(min_c/v) for k,v in f_comb_count.items()}
            rb.generate_puzzles(weight)
        else:
            rb.generate_puzzles()
        # if unique_test_pattern flag is set, and split is 0 (which indicates the task is test),
        # only take the same test patterns as before
        # also assert that the relation - test is present
        if args.unique_test_pattern and split == 0 and len(prev_patterns) > 0 and len(prev_patterns[args.relation_length]['test']) > 0:
            # if all these conditions met, prune the puzzles
            todel = []
            for pid,puzzle in rb.puzzles.items():
                if puzzle.relation_comb not in prev_patterns[args.relation_length]['test']:
                    todel.append(pid)
            for pid in todel:
                del rb.puzzles[pid]
        # now we have got the puzzles, assign the templators
        for pid, puzzle in rb.puzzles.items():
            if puzzle.relation_comb not in f_comb_count:
                f_comb_count[puzzle.relation_comb] = 0
            f_comb_count[puzzle.relation_comb] += 1
            pb.update(1)
            stories_left -= 1
        # store the puzzles
        all_puzzles.update(rb.puzzles)
        rb.reset_puzzle()
        rb.anc.next_flip()
    pb.close()
    print("Puzzles created. Now splitting train and test on pattern level")
    print("Number of unique puzzles : {}".format(len(all_puzzles)))
    pattern_puzzles = {}
    for pid, pz in all_puzzles.items():
        if pz.relation_comb not in pattern_puzzles:
            pattern_puzzles[pz.relation_comb] = []
        pattern_puzzles[pz.relation_comb].append(pid)
    print("Number of unique patterns : {}".format(len(pattern_puzzles)))
    train_puzzles = []
    test_puzzles = []
    sp = int(len(pattern_puzzles) * split)
    all_patterns = list(pattern_puzzles.keys())

    no_pattern_overlap = not args.holdout
    # if k=2, then set no_pattern_overlap=True
    if args.relation_length == 2:
        no_pattern_overlap = True

    if not no_pattern_overlap:
        # for case > 3, strict no pattern overlap
        train_patterns = all_patterns[:sp]
        pzs = [pattern_puzzles[p] for p in train_patterns]
        pzs = [s for p in pzs for s in p]
        train_puzzles.extend(pzs)
        test_patterns = all_patterns[sp:]
        pzs = [pattern_puzzles[p] for p in test_patterns]
        pzs = [s for p in pzs for s in p]
        test_puzzles.extend(pzs)
    else:
        # for case of 2, pattern overlap but templators are different
        # In this case, we have overlapping patterns, first choose the overlapping patterns
        # we directly split on puzzle level
        train_patterns = all_patterns
        test_patterns = all_patterns[sp:]
        pzs_train = []
        pzs_test = []
        for pattern in all_patterns:
            pz = pattern_puzzles[pattern]
            if pattern in test_patterns:
                # now split - hacky way
                sz = int(len(pz) * (split - 0.2))
                pzs_train.extend(pz[:sz])
                pzs_test.extend(pz[sz:])
            else:
                pzs_train.extend(pz)
        train_puzzles.extend(pzs_train)
        test_puzzles.extend(pzs_test)

    print("# Train puzzles : {}".format(len(train_puzzles)))
    print("# Test puzzles : {}".format(len(test_puzzles)))
    pb = tqdm(total=len(all_puzzles))
    # saving in csv
    for pid, puzzle in all_puzzles.items():
        task_split = ''
        if pid in train_puzzles:
            task_split = 'train'
            templator = templatorClass(templates=train_templates, family=puzzle.anc.family_data)
        elif pid in test_puzzles:
            task_split = 'test'
            templator = templatorClass(templates=test_templates, family=puzzle.anc.family_data)
        else:
            AssertionError("pid must be either in train or test")
        story_text = puzzle.generate_text(stype='story', combination_length=combination_length, templator=templator)
        fact_text = puzzle.generate_text(stype='fact', combination_length=combination_length, templator=templator)
        story = story_text + fact_text
        story = random.sample(story, len(story))
        story = ' '.join(story)
        clean_story = ' '.join(story_text)
        target_text = puzzle.generate_text(stype='target', combination_length=1, templator=templator)

        story_key_edges = puzzle.get_story_relations(stype='story') + puzzle.get_story_relations(stype='fact')
        puzzle.convert_node_ids(stype='story')
        puzzle.convert_node_ids(stype='fact')
        story_keys_changed_ids = puzzle.get_sorted_story_edges(stype='story') + puzzle.get_sorted_story_edges(stype='fact')
        query_edge = puzzle.get_sorted_query_edge()

        genders = puzzle.get_name_gender_string()

        rows.append([pid, story, puzzle.query_text, '', puzzle.target_edge_rel, target_text,
                     clean_story, puzzle.proof_trace, puzzle.relation_comb, task_name, story_keys_changed_ids,
                     story_key_edges, query_edge, genders, '', puzzle.story_sort_dict, task_split])
        pb.update(1)
    pb.close()

    print("{} ancestries created".format(anc_num))
    print("Number of unique patterns : {}".format(len(f_comb_count)))
    return columns, rows, all_puzzles, train_patterns, test_patterns


def test_run(args):
    store = Store(args)
    anc = Ancestry(args, store)
    rb = RelationBuilder(args, store, anc)
    rb.num_rel = 3
    all_patterns = set()
    while True:
        for j in range(len(anc.family_data.keys())):
            rb.build()
            up = rb.unique_patterns()
            all_patterns.update(up)
            print(len(all_patterns))
            rb.reset_puzzle()
        if not rb.anc.next_flip():
            break
    print("Number of unique puzzles : {}".format(len(all_patterns)))

    rb.add_facts()
    rb.generate_puzzles()
    print("Generated {} puzzles".format(len(rb.puzzles)))
    pid = random.choice(list(rb.puzzles.keys()))
    print(rb.puzzles[pid])

def main(args):
    store = Store(args)
    header, rows = generate_rows(args, store)
    df = pd.DataFrame(columns=header, data=rows)
    # split test train
    msk = np.random.rand(len(df)) > args.test
    train_df = df[msk]
    test_df = df[~msk]
    train_df.to_csv(args.output + '_train.csv')
    test_df.to_csv(args.output + '_test.csv')

if __name__ == '__main__':
    args = get_args()
    test_run(args)
    #main(args)








