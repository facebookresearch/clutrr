"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

## Note: With these current args (max level 3, min_child = max_child = 4), its only possible to generate
## upto 8 relations in my cpu. The code is not optimized yet.

import argparse

def get_args(command=None):
    parser = argparse.ArgumentParser()
    # graph parameters
    parser.add_argument("--max_levels", default=3, type=int, help="max number of levels")
    parser.add_argument("--min_child", default=4, type=int, help="max number of children per node")
    parser.add_argument("--max_child", default=4, type=int, help="max number of children per node")
    parser.add_argument("--p_marry", default=1.0, type=float, help="Probability of marriage among nodes")
    # story parameters
    parser.add_argument("--boundary",default=True, action='store_true', help='Boundary in entities')
    parser.add_argument("--output", default="gen_m3", type=str, help='Prefix of the output file')
    # Arguments not used now, use `--train_tasks` to set the task type and relation length
    # parser.add_argument("--relation_length", default=3, type=int, help="Max relation path length")
    # noise choices
    # parser.add_argument("--noise_support", default=False, action='store_true',
    #                     help="Noise type: Supporting facts")
    # parser.add_argument("--noise_irrelevant", default=False, action='store_true',
    #                     help="Noise type: Irrelevant facts")
    # parser.add_argument("--noise_disconnected", default=False, action='store_true',
    #                     help="Noise type: Disconnected facts")
    # parser.add_argument("--noise_attributes", default=False, action='store_true',
    #                     help="Noise type: Random attributes")
    # store locations
    parser.add_argument("--rules_store", default="rules_store.yaml", type=str, help='Rules store')
    parser.add_argument("--relations_store", default="relations_store.yaml", type=str, help='Relations store')
    parser.add_argument("--attribute_store", default="attribute_store.json", type=str, help='Attributes store')
    # task
    parser.add_argument("--train_tasks", default="1.3", type=str, help='Define which task to create dataset for, including the relationship length, comma separated')
    parser.add_argument("--test_tasks", default="1.3", type=str, help='Define which tasks including the relation lengths to test for, comma separaated')
    parser.add_argument("--train_rows", default=100, type=int, help='number of train rows')
    parser.add_argument("--test_rows", default=100, type=int, help='number of test rows')
    parser.add_argument("--memory", default=1, type=float, help='Percentage of tasks which are just memory retrieval')
    parser.add_argument("--data_type", default="train", type=str, help='train/test')
    # question type
    parser.add_argument("--question", default=0, type=int, help='Question type. 0 -> relational, 1 -> yes/no')
    # others
    # parser.add_argument("--min_distractor_relations", default=8, type=int, help="Distractor relations about entities")
    parser.add_argument("-v","--verbose", default=False, action='store_true',
                        help='print the paths')
    parser.add_argument("-t","--test_split", default=0.2, help="Testing split")
    parser.add_argument("--equal", default=False, action='store_true',
                        help="Make sure each pattern is equal. Warning: Time complexity of generation increases if this flag is set.")
    parser.add_argument("--analyze", default=False, action='store_true', help="Analyze generated files")
    parser.add_argument("--mturk", default=False, action='store_true', help='prepare data for mturk')
    parser.add_argument("--holdout", default=False, action='store_true', help='if true, then hold out unique patterns in the test set')
    parser.add_argument("--data_name", default='', type=str, help='Dataset name')
    parser.add_argument("--use_mturk_template", default=False, action='store_true', help='use the templating data for mturk')
    parser.add_argument("--template_length", type=int, default=2, help="Max Length of the template to substitute")
    parser.add_argument("--template_file", type=str, default="amt_placeholders_clean.json", help="location of placeholders")
    parser.add_argument("--template_split", default=True, action='store_true', help='Split on template level')
    parser.add_argument("--combination_length", type=int, default=1, help="number of relations to combine together")
    parser.add_argument("--output_dir", type=str, default="data", help="output_dir")
    parser.add_argument("--store_full_puzzles", default=False, action='store_true',
                        help='store the full puzzle data in puzzles.pkl file. Warning: may take considerable amount of disk space!')
    parser.add_argument("--unique_test_pattern", default=False, action='store_true', help="If true, have unique patterns generated in the first gen,  and then choose from it.")


    if command:
        return parser.parse_args(command.split(' '))
    else:
        return parser.parse_args()