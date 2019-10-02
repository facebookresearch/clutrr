"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

# main file which defines the tasks
from clutrr.args import get_args
from clutrr.generator import generate_rows
from clutrr.store.store import Store
import pandas as pd
import glob
import copy
import uuid
import os
import json
import shutil
import sys
import nltk
from nltk.tokenize import word_tokenize
import pickle as pkl
import requests
import hashlib
import zipfile

# check if nltk.punkt is installed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

logPath = '../logs/'
fileName = 'data'
# sha of the placeholder files
SHA_SUM = 'ed2264836bb17fe094dc21fe6bb7492b000df520eb86f8e60b8441121f8ff924'
download_url = "https://cs.mcgill.ca/~ksinha4/data/"

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()

class Clutrr:
    """
    Data Generation Script for the paper
    "CLUTRR - A benchmark suite for inductive reasoning on text"
    """
    def __init__(self, args):
        self.args = self._init_vars(args)
        # store the unique patterns for each relation here
        self.unique_patterns = {}
        self.setup()

    def generate(self, choice, args, num_rows=0, data_type='train', multi=False, split=None):
        """
        Choose the task and the relation length
        Return the used args for storing
        :param choice:
        :param args:
        :param num_rows:
        :param data_type:
        :param multi:
        :return:
        """
        args = copy.deepcopy(args)
        args.num_rows = num_rows
        args.data_type = data_type
        if not multi:
            task, relation_length = choice.split('.')
            task_name = 'task_{}'.format(task)
            logger.info("mode : {}, task : {}, rel_length : {}".format(data_type, task_name, relation_length))
            task_method = getattr(self, task_name, lambda: "Task {} not implemented".format(choice))
            args = task_method(args)
            args.relation_length = int(relation_length)
            store = Store(args)
            columns, rows, all_puzzles, train_patterns, test_patterns = generate_rows(args,
                        store, task_name  + '.{}'.format(relation_length), split=split, prev_patterns=self.unique_patterns)
            self.unique_patterns[int(relation_length)] = {
                'train': train_patterns,
                'test': test_patterns
            }
            return (columns, rows, all_puzzles), args

        else:
            rows = []
            columns = []
            puzzles = {}
            for ch in choice:
                task, relation_length = ch.split('.')
                task_name = 'task_{}'.format(task)
                logger.info("task : {}, rel_length : {}".format(task_name, relation_length))
                task_method = getattr(self, task_name, lambda: "Task {} not implemented".format(choice))
                args = task_method(args)
                args.relation_length = int(relation_length)
                store = Store(args)
                columns,r,pz = generate_rows(args, store, task_name + '.{}'.format(relation_length))
                rows.extend(r)
                puzzles.update(pz)
            return ((columns, rows, puzzles), args)

    def run_task(self):
        """
        Default dispatcher method
        """
        args = self.args
        train_rows = args.train_rows
        test_rows = args.test_rows
        train_choices = args.train_tasks.split(',')
        test_choices = args.test_tasks.split(',')
        all_choices = []
        for t in train_choices:
            if t not in all_choices:
                all_choices.append(t)
        for t in test_choices:
            if t not in all_choices:
                all_choices.append(t)
        train_datas = []
        for choice in all_choices:
            if choice in train_choices:
                # split
                choice_split = train_rows / (train_rows + test_rows)
                num_rows = train_rows + test_rows
            else:
                # test, no split
                choice_split = 0.0
                num_rows = test_rows
            print("Split : {}".format(choice_split))
            train_datas.append(self.generate(choice, args, num_rows=num_rows, data_type='train', split=choice_split))

        self.store(train_datas, None, args)

    def assign_name(self, args, task_name):
        """
        Create a name for the datasets:
            - training file should end with _train
            - testing file should end with _test
            - each file name should have an unique hex
        :param args:
        :return:
        """
        name = '{}_{}.csv'.format(task_name, args.data_type)
        return name

    def store(self, train_data, test_data, args):
        """
        Take the dataset and do the following:
        - Create a name for the files
        - Create a folder and put the files in
        - Write the config in a file and put it in the folder
        - Compute the hash of the train and test files and store it in a file
        :param train_data list of rows
        :param test_data list of list of rows
        :return:
        """
        train_tasks = args.train_tasks.split(',')
        all_puzzles = {}
        train_df = []
        test_df = []
        for i, td in enumerate(train_data):
            train_rows_puzzles, train_args = td
            assert len(train_rows_puzzles) == 3
            train_rows, train_puzzles = train_rows_puzzles[:-1], train_rows_puzzles[-1]
            trdfs = [r for r in train_rows[1] if r[-1] == 'train']
            tsdfs = [r for r in train_rows[1] if r[-1] == 'test']
            train_df.append(pd.DataFrame(columns=train_rows[0], data=trdfs))
            test_df.append(pd.DataFrame(columns=train_rows[0], data=tsdfs))

        train_df = pd.concat(train_df)
        test_df = pd.concat(test_df)
        logger.info("Training rows : {}".format(len(train_df)))
        logger.info("Testing rows : {}".format(len(test_df)))

        # prepare configs
        all_config = {}
        train_fl_name = self.assign_name(train_args, args.train_tasks)
        all_config['train_task'] = {args.train_tasks: train_fl_name}
        all_config['test_tasks'] = {}
        test_fl_names = []
        all_config['args'] = {}
        all_config['args'][train_fl_name] = vars(train_args)
        test_tasks = args.test_tasks.split(',')
        test_dfs = []
        for test_task in test_tasks:
            train_args.data_type = 'test'
            test_fl_name = self.assign_name(train_args,test_task)
            all_config['args'][test_fl_name] = vars(train_args)
            test_fl_names.append(test_fl_name)
            test_dfs.append(test_df[test_df.task_name == 'task_'+test_task])

        base_path = os.path.abspath(os.pardir)
        # derive folder name as a random selection of characters
        directory = ''
        while True:
            folder_name = 'data_{}'.format(str(uuid.uuid4())[:8])
            directory = os.path.join(base_path, args.output_dir, folder_name)
            if not os.path.exists(directory):
                os.makedirs(directory)
                break
        train_df.to_csv(os.path.join(directory, train_fl_name))
        for i,test_fl_name in enumerate(test_fl_names):
            test_df = test_dfs[i]
            test_df.to_csv(os.path.join(directory, test_fl_name))
        # dump config
        json.dump(all_config, open(os.path.join(directory, 'config.json'),'w'))
        if args.store_full_puzzles:
            # dump all puzzles
            pkl.dump(all_puzzles, open(os.path.join(directory, 'puzzles.pkl'),'wb'), protocol=-1)
        shutil.make_archive(directory, 'zip', directory)

        logger.info("Created dataset in {}".format(directory))
        self.analyze_data(directory)
        if args.mturk:
            self.keep_unique(directory)


    def analyze_data(self, directory):
        """
        Analyze a given directory
        :param directory:
        :return:
        """
        all_files = glob.glob(os.path.join(directory,'*.csv'))
        for fl in all_files:
            logger.info("Analyzing file {}".format(fl))
            df = pd.read_csv(fl)
            df['word_len'] = df.story.apply(lambda x: len(word_tokenize(x)))
            df['word_len_clean'] = df.clean_story.apply(lambda x: len(word_tokenize(x)))
            print("Max words : ", df.word_len.max())
            print("Min words : ", df.word_len.min())
            print("For clean story : ")
            print("Max words : ", df.word_len_clean.max())
            print("Min words : ", df.word_len_clean.min())
        logger.info("Analysis complete")

    def keep_unique(self, directory, num=1):
        """
        Keep num unique rows for each pattern. Handy for Mturk collection.
        :param num:
        :return:
        """
        all_files = glob.glob(os.path.join(directory, '*.csv'))
        for fl in all_files:
            df = pd.read_csv(fl)
            uniq_patterns = df['f_comb'].unique()
            udf = []
            for up in uniq_patterns:
                # randomly select one row for this unique pattern
                rd = df[df['f_comb'] == up].sample(num)
                udf.append(rd)
            udf = pd.concat(udf)
            udf.to_csv(fl)



    def _init_vars(self, args):
        args.noise_support = False
        args.noise_irrelevant = False
        args.noise_disconnected = False
        args.noise_attributes = False
        args.memory = 0
        return args

    def task_1(self, args):
        """
        Basic family relation without any noise
        :return:
        """
        args.output += '_task1'
        return args

    def task_2(self, args):
        """
        Family relation with supporting facts
        :return:
        """
        args.noise_support = True
        args.output += '_task2'
        return args

    def task_3(self, args):
        """
        Family relation with irrelevant facts
        :return:
        """
        args.noise_irrelevant = True
        args.output += '_task3'
        return args

    def task_4(self, args):
        """
        Family relation with disconnected facts
        :return:
        """
        args.noise_disconnected = True
        args.output += '_task4'
        return args

    def task_5(self, args):
        """
        Family relation with all facts
        :return:
        """
        args.noise_support = True
        args.noise_disconnected = True
        args.noise_disconnected = True
        args.output += '_task5'
        return args

    def task_6(self, args):
        """
        Family relation with only memory retrieval
        :param args:
        :return:
        """
        args.memory = 1.0
        args.output += '_task6'
        return args

    def task_7(self, args):
        """
        Family relation with mixed memory and reasoning
        :param args:
        :return:
        """
        args.memory = 0.5
        args.output += '_task7'
        return args

    def setup(self):
        """
        Download placeholders and update args
        :return:
        """
        placeholder_zip = "cleaned_placeholders.zip"
        placeholder_url = download_url + placeholder_zip
        base_path = os.path.abspath(os.pardir)
        placeholder_loc = os.path.join(base_path, placeholder_zip)
        if os.path.exists(placeholder_loc):
            print("downloaded placeholder data exists")
        else:
            print("Downloading placeholder data")
            r = requests.get(placeholder_url)
            with open(placeholder_loc, 'wb') as f:
                f.write(r.content)
            # check shasum
            sha1 = hashlib.sha256()
            BUF_SIZE = 65536
            with open(placeholder_loc, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    sha1.update(data)
            print("sha256 : {}".format(sha1.hexdigest()))
            print("checking ...")
            if sha1.hexdigest() != SHA_SUM:
                raise AssertionError("downloaded corrupt data, sha256 doesn't match")
            print("Data valid")
            # extract zip
            with zipfile.ZipFile(placeholder_loc, "r") as zip_ref:
                zip_ref.extractall(os.path.join(base_path, 'clutrr'))
        # set args
        self.args.template_file = "cleaned_placeholders/amt_placeholders_clean"


if __name__ == '__main__':
    args = get_args()
    logger.info("Data generation started for configurations : ")
    logger.info('\ntogrep : {0}\n'.format(sys.argv[1:]))
    cl = Clutrr(args)
    cl.run_task()
    logger.info("\ntogrep : Data generation done {0}\n".format(sys.argv[1:]))
    logger.info("-----------------------------------------------------")
