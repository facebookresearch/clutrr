# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

#!/bin/sh

export CLUTRR_OUTPUT_DIR=data_emnlp_only_holdout

# generalization tasks

#python main.py --train_tasks 1.2,1.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - clean" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 2.2,2.3 --test_tasks 2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,2.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - support" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 3.2,3.3 --test_tasks 3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - noise a." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 4.2,4.3 --test_tasks 4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,4.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - noise b." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 5.2,5.3 --test_tasks 5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,5.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - mix of support and noise" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 7.2,7.3 --test_tasks 7.2,7.3,7.4,7.5,7.6,7.7,7.8,7.9,7.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - memory" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &

#python main.py --train_tasks 1.2,1.4 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - clean" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 2.2,2.4 --test_tasks 2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,2.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - support" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 3.2,3.4 --test_tasks 3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - noise a." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 4.2,4.4 --test_tasks 4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,4.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - noise b." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 5.2,5.4 --test_tasks 5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,5.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - mix of support and noise" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 7.2,7.4 --test_tasks 7.2,7.3,7.4,7.5,7.6,7.7,7.8,7.9,7.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - memory" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &

# Hard version
# Systematic Generalization
#python main.py --train_tasks 1.2,1.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 5000 --test_rows 100 --equal --holdout --template_split --data_name "Generalization - holdout - clean" --use_mturk_template --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 1.2,1.3,1.4 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 5000 --test_rows 100 --equal --holdout --template_split --data_name "Generalization - holdout - clean, 2,3 and 4" --use_mturk_template --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 1.2,1.3,1.4,1.5 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 5000 --test_rows 100 --equal --holdout --template_split --data_name "Generalization - holdout - clean, 2,3 and 4" --use_mturk_template --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 1.2,1.3,1.4,1.5,1.6 --test_tasks 1.2,1.3,1.4,1.5,1.6 --train_rows 5000 --test_rows 100 --equal --holdout --template_split --data_name "Generalization - holdout - clean" --use_mturk_template --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &

# Robust Reasoning
#python main.py --train_tasks 1.2,1.3 --test_tasks 1.2,1.3,2.3,3.3,4.3 --train_rows 5000 --test_rows 100 --equal --holdout --template_split --use_mturk_template --data_name "Robust Reasoning - clean - AMT" --unique_test_pattern --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 2.2,2.3 --test_tasks 2.2,1.3,2.3,3.3,4.3 --train_rows 5000 --test_rows 100 --equal --holdout --template_split --use_mturk_template --data_name "Robust Reasoning - supporting - AMT" --unique_test_pattern --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 3.2,3.3 --test_tasks 3.2,1.3,2.3,3.3,4.3 --train_rows 5000 --test_rows 100 --equal --holdout --template_split --use_mturk_template --data_name "Robust Reasoning - noise a. - AMT" --unique_test_pattern --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 4.2,4.3 --test_tasks 4.2,1.3,2.3,3.3,4.3 --train_rows 5000 --test_rows 100 --equal --holdout --template_split --use_mturk_template --data_name "Robust Reasoning - noise b.- AMT" --unique_test_pattern --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &

# Easy version
# Systematic Generalization
#python main.py --train_tasks 1.2,1.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 5000 --test_rows 500 --equal --data_name "Generalization - holdout - clean" --use_mturk_template --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 1.2,1.3,1.4 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 5000 --test_rows 500 --equal --data_name "Generalization - holdout - clean, 2,3 and 4" --use_mturk_template --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 1.2,1.3,1.4,1.5 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 5000 --test_rows 500 --equal --data_name "Generalization - holdout - clean, 2,3 and 4" --use_mturk_template --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 1.2,1.3,1.4,1.5,1.6 --test_tasks 1.2,1.3,1.4,1.5,1.6 --train_rows 5000 --test_rows 500 --equal --data_name "Generalization - holdout - clean" --use_mturk_template --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &

# Robust Reasoning
python main.py --train_tasks 1.2,1.3 --test_tasks 1.2,1.3,2.3,3.3,4.3 --train_rows 5000 --test_rows 500 --equal --holdout --use_mturk_template --data_name "Robust Reasoning - clean - AMT" --unique_test_pattern --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
python main.py --train_tasks 2.2,2.3 --test_tasks 2.2,1.3,2.3,3.3,4.3 --train_rows 5000 --test_rows 500 --equal --holdout --use_mturk_template --data_name "Robust Reasoning - supporting - AMT" --unique_test_pattern --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
python main.py --train_tasks 3.2,3.3 --test_tasks 3.2,1.3,2.3,3.3,4.3 --train_rows 5000 --test_rows 500 --equal --holdout --use_mturk_template --data_name "Robust Reasoning - noise a. - AMT" --unique_test_pattern --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
python main.py --train_tasks 4.2,4.3 --test_tasks 4.2,1.3,2.3,3.3,4.3 --train_rows 5000 --test_rows 500 --equal --holdout --use_mturk_template --data_name "Robust Reasoning - noise b.- AMT" --unique_test_pattern --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &

wait


#python main.py --train_tasks 2.2,2.3 --test_tasks 2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,2.10 --train_rows 5000 --test_rows 100 --equal --holdout 2.3 --data_name "Generalization - holdout - support" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 3.2,3.3 --test_tasks 3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10 --train_rows 5000 --test_rows 100 --equal --holdout 3.3 --data_name "Generalization - holdout - noise a." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 4.2,4.3 --test_tasks 4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,4.10 --train_rows 5000 --test_rows 100 --equal --holdout 4.3 --data_name "Generalization - holdout - noise b." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 5.2,5.3 --test_tasks 5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,5.10 --train_rows 5000 --test_rows 100 --equal --holdout 5.3 --data_name "Generalization - holdout - mix of support and noise" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 7.2,7.3 --test_tasks 7.2,7.3,7.4,7.5,7.6,7.7,7.8,7.9,7.10 --train_rows 5000 --test_rows 100 --equal --holdout 7.3 --data_name "Generalization - holdout - memory" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &


#python main.py --train_tasks 1.2,1.3,1.4 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 3000 --test_rows 100 --equal --holdout 1.4 --data_name "Generalization - clean" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 2.2,2.3,2.4 --test_tasks 2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,2.10 --train_rows 3000 --test_rows 100 --equal --holdout 2.4 --data_name  "Generalization - support" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 3.2,3.3,3.4 --test_tasks 3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10 --train_rows 3000 --test_rows 100 --equal --holdout 3.4 --data_name  "Generalization - noise a." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 4.2,4.3,4.4 --test_tasks 4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,4.10 --train_rows 3000 --test_rows 100 --equal --holdout 4.4 --data_name "Generalization - noise b." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 5.2,5.3,5.4 --test_tasks 5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,5.10 --train_rows 3000 --test_rows 100 --equal --holdout 5.4 --data_name "Generalization - mix of support and noise" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 7.2,7.3,7.4 --test_tasks 7.2,7.3,7.4,7.5,7.6,7.7,7.8,7.9,7.10 --train_rows 3000 --test_rows 100 --equal --holdout 7.4 --data_name "Generalization - memory" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &


# basic reasoning tasks

#python main.py --train_tasks 1.2,1.3 --test_tasks 2.3,3.3,4.3 --train_rows 5000 --test_rows 100 --equal --use_mturk_template --data_name "Robust Reasoning - clean - AMT" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 2.2,2.3 --test_tasks 1.3,3.3,4.3 --train_rows 5000 --test_rows 100 --equal --use_mturk_template --data_name "Robust Reasoning - supporting - AMT" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 3.2,3.3 --test_tasks 1.3,2.3,4.3 --train_rows 5000 --test_rows 100 --equal --use_mturk_template --data_name "Robust Reasoning - noise a. - AMT" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 4.2,4.3 --test_tasks 1.3,2.3,3.3 --train_rows 5000 --test_rows 100 --equal --use_mturk_template --data_name "Robust Reasoning - noise b.- AMT" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &

#python main.py --train_tasks 3.2,3.3,4.2,4.3 --test_tasks 1.3,2.3,7.3 --train_rows 2500 --test_rows 100 --equal --data_name "Robust Reasoning - noise a. and b." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 1.2,1.3,4.2,4.3 --test_tasks 1.3,3.3,7.3 --train_rows 2500 --test_rows 100 --equal --data_name "Robust Reasoning - clean and noise b." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 1.2,1.3,3.2,3.3 --test_tasks 1.3,4.3,7.3 --train_rows 2500 --test_rows 100 --equal --data_name "Robust Reasoning - clean and noise a." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 1.2,1.3,7.2,7.3 --test_tasks 2.3,3.3,4.3 --train_rows 2500 --test_rows 100 --equal --data_name "Robust Reasoning - clean and memory" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 3.2,3.3,7.2,7.3 --test_tasks 1.3,2.3,4.3 --train_rows 2500 --test_rows 100 --equal --data_name "Robust Reasoning - noise a. and memory" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 4.2,4.3,7.2,7.3 --test_tasks 1.3,2.3,3.3 --train_rows 2500 --test_rows 100 --equal --data_name "Robust Reasoning - noise b. and memory" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &


# how mixed training helps generalization

#python main.py --train_tasks 3.2,3.3,4.2,4.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 2500 --test_rows 100 --equal --data_name "Generalization with Reasoning - noise a. and noise b." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 1.2,1.3,4.2,4.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 2500 --test_rows 100 --equal --data_name "Generalization with Reasoning - clean and noise b." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 1.2,1.3,3.2,3.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 2500 --test_rows 100 --equal --data_name "Generalization with Reasoning - clean and noise a." --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 1.2,1.3,7.2,7.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 2500 --test_rows 100 --equal --data_name "Generalization with Reasoning - clean and memory" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 3.2,3.3,7.2,7.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 2500 --test_rows 100 --equal --data_name "Generalization with Reasoning - noise a. and memory" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &
#python main.py --train_tasks 4.2,4.3,7.2,7.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 2500 --test_rows 100 --equal --data_name "Generalization with Reasoning - noise b. and memory" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &

# holdout
# python main.py --train_tasks 1.2,1.3 --test_tasks 1.2,1.3 --train_rows 5000 --test_rows 100 --equal --holdout 1.3 --data_name "Generalization - holdout - 2 & 3" --output_dir $CLUTRR_OUTPUT_DIR >/dev/null 2>&1 &

# python utils/web.py --output_dir /private/home/koustuvs/clutrr-2.0/$CLUTRR_OUTPUT_DIR
