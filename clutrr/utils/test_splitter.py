"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

# Split the test files into their own task specific files
# Not required in actual data generation
import pandas as pd
import os
import glob
import json
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # graph parameters
    parser.add_argument("--data_folder", default='data_emnlp', type=str, help="data folder")
    args = parser.parse_args()
    base_path = os.path.abspath(os.path.join(os.pardir, os.pardir))
    print(base_path)
    # search for directories
    dirs = glob.glob(os.path.join(base_path, args.data_folder, '*'))
    dirs = [dir for dir in dirs if os.path.isdir(dir)]
    print("Found {} directories".format(len(dirs)))
    print(dirs)
    for folder in dirs:
        # read config file
        config = json.load(open(os.path.join(folder, 'config.json')))
        # get test_file
        test_files = glob.glob(os.path.join(folder, '*_test.csv'))
        # get splittable test files
        test_files = [t for t in test_files if len(t.split(',')) > 1]
        for test_file in test_files:
            df = pd.read_csv(test_file)
            test_fl_name = test_file.split('/')[-1]
            tasks = df.task_name.unique()
            for task in tasks:
                dft = df[df.task_name == task]
                tname = task.split('task_')[-1]
                flname = tname + '_test.csv'
                dft.to_csv(os.path.join(folder, flname))
                config['args'][flname] = config['args'][test_fl_name]
                config['test_tasks'][tname] = test_fl_name
            del config['args'][test_fl_name]
        json.dump(config, open(os.path.join(folder, 'config.json'),'w'))
        # backup the original test_files
        for test_file in test_files:
            os.rename(test_file, test_file.replace('_test','_backupt'))
    print("splitting done")
