#!/bin/bash
DATA_LOC=/Users/koustuvs/mlp/cluttr_data
NUM_TRAIN=1000
NUM_VALID=100
NUM_TEST=100
# Task description
TRAIN_DESCRIPTOR_LENGTHS=\'2,3,4\'
VAL_DESCRIPTOR_LENGTHS=\'3,4\'
TEST_DESCRIPTOR_LENGTHS=\'3,4\'
# generate glc
python glc/glc.py save_loc=$DATA_LOC rule_store=glc/rule_bases/clutrr world_prefix=rule num_train_graphs=$((NUM_TRAIN*2)) num_valid_graphs=$((NUM_VALID*2)) num_test_graphs=$((NUM_TEST*2)) train_descriptor_lengths=$TRAIN_DESCRIPTOR_LENGTHS val_descriptor_lengths=$VAL_DESCRIPTOR_LENGTHS test_descriptor_lengths=$TEST_DESCRIPTOR_LENGTHS
python clutrr/generator_glc.py data_loc=$DATA_LOC num_train=$NUM_TRAIN num_valid=$NUM_VALID num_test=$NUM_TEST
