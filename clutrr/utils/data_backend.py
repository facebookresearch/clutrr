"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

# File which was used in data collection from AMT using ParlAI-Mturk.
# Wrapper to communicate with backend database
# The database (Mongo) is used to maintain a set of collections
#   - data we need to annotate : gold
#   - dump for annotated data : mturk  - this should also contain our manual tests
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
import random
import glob
import schedule
import time
import datetime
import nltk
import subprocess
from numpy.random import choice
import argparse

KOUSTUV_ID = "A1W0QQF93UM08"
PORT = 27017
COLLECTION = 'amt_study'
GOLD_TABLE = 'gold'
MTURK_TABLE = 'mturk'
REVIEW_TABLE = 'review' # special table only used when we use review-only mode
USER_BASE = '/private/home/koustuvs/'
CLUTRR_BASE = USER_BASE + 'mlp/clutrr-2.0/'
SQLITE_BASE = CLUTRR_BASE + 'mturk/parlai/mturk/core/run_data/'
DRIVE_PATH = USER_BASE + 'Google Drive/clutrr/'

class DB:
    def __init__(self, host='localhost', port=PORT, collection=COLLECTION, test_prob=0.0):
        # initiate the db connection
        self.client = MongoClient(host, port)
        #print("Connected to backend MongoDB data at {}:{}".format(host, port))
        self.gold = self.client[collection][GOLD_TABLE]
        self.mturk = self.client[collection][MTURK_TABLE]
        self.review = self.client[collection][REVIEW_TABLE]
        self.test_prob = test_prob
        self.test_worker = KOUSTUV_ID

    def _read_csv(self, path):
        assert path.endswith('.csv')
        return pd.read_csv(path)

    def upload(self, data_path, db='gold'):
        """
        Given a csv file, upload the entire dataframe in the particular db
        :param data:
        :param db:
        :return:
        """
        print("Reading {}".format(data_path))
        data = self._read_csv(data_path)
        records = data.to_dict(orient='records')
        # add used counter if gold and test
        # add reviewed counter if mturk
        num_records = len(records)
        print("Number of records found : {}".format(len(records)))
        for rec in records:
            if db == 'gold':
                rec['used'] = 0
            else:
                rec['reviewed'] = 0
            sents = nltk.sent_tokenize(rec['story'])
            rec['relation_length'] = len(sents)
        mdb = getattr(self, db)
        # prune the records which are already present in the database
        keep_idx = []
        for rec_idx, rec in enumerate(records):
            fd = mdb.find({'id': rec['id']}).count()
            if fd == 0:
                keep_idx.append(rec_idx)
        records = [records[idx] for idx in keep_idx]
        num_kept = len(records)
        print("Number of records already in db : {}".format(num_records - num_kept))
        if len(records) > 0:
            r = mdb.insert_many(records)
        print("Inserted {} records in db {}".format(len(records), db))

    def update_gender(self, data_path):
        """
        Update the genders
        :param data_path:
        :return:
        """
        print("Reading {}".format(data_path))
        data = self._read_csv(data_path)
        for i, row in data.iterrows():
            self.mturk.update_many({'gold_id': ObjectId(row['_id'])}, {"$set": {'genders': row['genders']}}, upsert=False)
        print('Updated {} records'.format(len(data)))

    def choose_relation(self):
        # unused records
        avg_used = list(self.gold.aggregate([{'$group': {'_id': '$relation_length', 'avg': {'$avg': '$used'}}}]))
        # normalize
        avg = [rel['avg'] for rel in avg_used]
        relations = [rel['_id'] for rel in avg_used]
        # dont server relation 3 for a moment
        #rel_idx = relations.index(3)
        #del relations[rel_idx]
        #del avg[rel_idx]
        print("Found {} distinct relations".format(relations))
        norm_avg = self._norm(avg)
        # inverse the probability
        delta = 0.01
        norm_avg = [1 / i + delta for i in norm_avg]
        norm_avg = self._norm(norm_avg)
        rand_relation = int(choice(relations, 1, p=norm_avg)[0])
        print("Choosing relation {}".format(rand_relation))
        return rand_relation

    def get_gold(self, rand_relation=None):
        """
        Find the gold record to annotate.
        Rotation policy: first randomly choose a relation_length, then choose the least used
        annotation
        :return:
        """
        if not rand_relation:
            rand_relation = self.choose_relation()
        print("Randomly choosing {}".format(rand_relation))
        record = self.gold.find_one({'relation_length': rand_relation}, sort=[("used",1)])
        return record

    def get_gold_by_id(self, id=''):
        """
        Get a specific gold record by id
        :param id:
        :return:
        """
        try:
            record = self.gold.find_one({'_id': ObjectId(id)})
        except:
            record = None
        return record

    def _norm(self, arr):
        s = sum(arr)
        return [r/s for r in arr]

    def get_peer(self, worker_id='test', relation_length=2):
        """
        Get an annotation which is not done by the current worker, and which isn't reviewed
        Also, no need to choose relation of length 1
        With some probability, choose our test records
        :param worker_id:
        :param relation_length:
        :return: None if no suitable candidate found
        """
        using_test = False
        record = None
        if relation_length == 1:
            relation_length = random.choice([2,3])
        print("Choosing records with test probability {}".format(self.test_prob))
        if random.uniform(0,1) <= self.test_prob:
            using_test = True
            record_cursor = self.mturk.find({'worker_id': self.test_worker, 'relation_length': relation_length},
                                            sort=[("used",1)])
            print("Choosing a test record to annotate")
        else:
            record_cursor = self.mturk.find({'worker_id': {"$nin": [worker_id, self.test_worker]}, 'relation_length': relation_length, 'used':1})
            print("Choosing a review record to annotate")
        rec_found = False
        if record_cursor.count() > 0:
            rec_found = True
        print("Found a record to annotate")
        if not using_test and not rec_found:
            # if no candidate peer is found, default to test
            record_cursor = self.mturk.find({'worker_id': self.test_worker, 'relation_length': relation_length},
                    sort=[("used",1)])
            print("No records found, reverting back to test")
        if record_cursor.count() > 0:
            record = random.choice(list(record_cursor))
        if not record:
            # did not find either candidate peer nor test, raise error
            raise FileNotFoundError("no candidate found in db")
        return record

    def save_review(self, record, worker_id, rating=0.0):
        """
        Save the review. If its correct, then 1.0, else 0.0.
        :param record:
        :param rating:
        :return:
        """
        assert 'reviews' in record
        assert 'reviewed_by' in record
        record['used'] = len(record['reviewed_by']) + 1
        record['reviewed_by'].append({worker_id: rating})
        self.mturk.update_one({'_id': record['_id']}, {"$set": record}, upsert=False)

    def save_annotation(self, record, worker_id):
        """ Save the user annotation
        """
        if 'worker_id' not in record:
            record['worker_id'] = ''
        record['worker_id'] = worker_id
        if 'reviews' not in record:
            record['reviews'] = 0
        record['reviews'] = 0
        if 'reviewed_by' not in record:
            record['reviewed_by'] = []
        record['reviewed_by'] = []
        record['used'] = 0
        # change the id
        record['gold_id'] = record['_id']
        del record['_id']
        self.mturk.insert_one(record)
        self.gold.update_one({'_id': record['gold_id']}, {'$inc': {'used': 1}}, upsert=False)

    def done_review(self, worker_id, assignment_id, task_group_id):
        """
        Mark with timestamp when a worker has done a review
        :param worker_id:
        :return:
        """
        self.review.insert_one({'worker_id':worker_id,
                                'assignment_id': assignment_id,
                                'task_group_id':task_group_id,
                                'accepted': ''})


    def import_data(self):
        path = CLUTRR_BASE + 'mturk_data/*'
        print("Checking the path: {}".format(path))
        files = glob.glob(path)
        print("Files found : {}".format(len(files)))
        for fl in files:
            if fl.endswith('gold.csv'):
                self.upload(fl, db='gold')
            if fl.endswith('mturk.csv'):
                self.upload(fl, db='mturk')

    def export(self, base_path=CLUTRR_BASE, batch_size=100):
        """
        Dump datasets into csv
        :return:
        """
        print("Exporting datasets ...")
        gold = pd.DataFrame(list(self.gold.find()))
        gold_path = os.path.join(base_path,"amt_gold.csv")
        mturk_path = base_path
        mturk = pd.DataFrame(list(self.mturk.find()))
        print("Gold : {} records to {}".format(len(gold), gold_path))
        print("Mturk : {} records to {}".format(len(mturk), mturk_path))
        gold.to_csv(gold_path)
        # save data in batches
        mturk_splits = splitDataFrameIntoSmaller(mturk, chunkSize=batch_size)
        for i, mturk_b in enumerate(mturk_splits):
            mturk_b.to_csv(os.path.join(mturk_path, "amt_mturk_{}.csv".format(i)))

    def export_mongodb(self, path=CLUTRR_BASE):
        """
        Export the entire mongodb dump to location, preferably a google drive
        :param path:
        :return:
        """
        print("Exporting local mongodb to {}".format(path))
        command = "mongodump --db {} --out {} --gzip".format(COLLECTION, path)
        res = subprocess.run(command.split(" "), stdout=subprocess.PIPE)
        print(res)

    def export_sqlite(self, path=CLUTRR_BASE, sqlite_path=SQLITE_BASE):
        """
        Zip and export the sqlite database in sqlite path
        :param path:
        :return:
        """
        print("Export local sqlite db to {}".format(path))
        command = "zip -q -r {}/run_data.zip {}".format(path, sqlite_path)
        res = subprocess.run(command.split(" "), stdout=subprocess.PIPE)
        print(res)


    def update_relation_length(self):
        print("Updating...")
        gold = self.gold.find({})
        up = 0
        for rec in gold:
            rec['relation_length'] = len(nltk.sent_tokenize(rec['story']))
            self.gold.update_one({'_id': rec['_id']}, {"$set": rec}, upsert=False)
            up += 1
        mturk = self.mturk.find({})
        for rec in mturk:
            rec['relation_length'] = len(nltk.sent_tokenize(rec['story']))
            self.mturk.update_one({'_id': rec['_id']}, {"$set": rec}, upsert=False)
            up += 1
        print("Updated {} records".format(up))

    def close_connections(self):
        #print("Closing connection")
        self.client.close()


def import_job():
    data = DB(port=PORT)
    data.import_data()
    data.close_connections()

def export_job(folder, batch_size=100):
    save_path = os.path.join(CLUTRR_BASE, folder)
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    data = DB(port=PORT)
    data.export(base_path=save_path, batch_size=batch_size)
    save_user_path = os.path.join(USER_BASE, folder)
    if not os.path.exists(save_user_path):
        os.mkdir(save_user_path)
    data.export(base_path=save_user_path, batch_size=batch_size)
    data.close_connections()

def backup_job():
    data = DB(port=PORT)
    data.export_mongodb()
    data.export_sqlite()

def info_job():
    data = DB(port=PORT)
    print("Generating statistics at {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    gold_c = data.gold.find({}).count()
    pending_c = data.gold.count_documents({'used':0})
    avg_used = list(data.gold.aggregate([{'$group': {'_id':None,'avg' : {'$avg' : '$used'}}}]))
    if len(avg_used) > 0:
        avg_used = avg_used[0]['avg']
    mturk_c = data.mturk.count_documents({})
    uniq_workers = len(data.mturk.find({}).distinct("worker_id"))
    mturk_c_1 = data.mturk.count_documents({'relation_length':1})
    gold_agg = list(data.gold.aggregate([{'$group': {'_id': {'relation_length': '$relation_length', 'f_comb': '$f_comb'},
                                                       'avg' : {'$avg' : '$used'}}}, {'$sort': {"_id.relation_length": 1}}]))
    mturk_reviews = list(data.mturk.aggregate([{'$group': {'_id': None, 'total_rev': {'$sum': {'$size': '$reviewed_by'}}}}]))

    for rec in gold_agg:
        if rec['_id']['relation_length'] != 3:
            print(rec['_id']['relation_length'], '\t', rec['_id']['f_comb'], '\t', rec['avg'])

    mturk_c_2 = data.mturk.count_documents({'relation_length':2})
    #gold_c_2_u = list(data.gold.aggregate([{'$group': {'_id':None,'relation_length':2, 'avg' : {'$avg' : '$used'}}}]))[0]['avg']

    mturk_c_3 = data.mturk.count_documents({'relation_length':3})
    #gold_c_3_u = list(data.gold.aggregate([{'$group': {'_id':None,'relation_length':3, 'avg' : {'$avg' : '$used'}}}]))[0]['avg']
    print("Number of gold data : {} \n ".format(gold_c) +
          "Number of pending rows to annotate : {} \n ".format(pending_c) +
          "Average times each gold row has been used : {} \n ".format(avg_used) +
          "Number of annotations given : {} \n".format(mturk_c) +
          "Unique workers : {}\n".format(uniq_workers) + 
          "Number of 1 relations annotated : {}\n".format(mturk_c_1) +  
          "Number of 2 relations annotated : {}\n".format(mturk_c_2) + 
          "Number of 3 relations annotated : {}\n".format(mturk_c_3) +
          "Total reviews provided : {}\n".format(mturk_reviews[0]['total_rev']))

def update_genders():
    data = DB(port=PORT)
    data.update_gender('/private/home/koustuvs/mlp/clutrr-2.0/amt_gold_gender.csv')
    data.close_connections()

def test_get_gold(k=100):
    data = DB(port=PORT)
    rel_chosen = {1:0,2:0,3:0}
    for i in range(k):
        record = data.get_gold()
        rel_chosen[record['relation_length']] +=1
    print(rel_chosen)
    data.close_connections()

def splitDataFrameIntoSmaller(df, chunkSize = 10000):
    listOfDf = list()
    numberChunks = len(df) // chunkSize + 1
    for i in range(numberChunks):
        listOfDf.append(df[i*chunkSize:(i+1)*chunkSize])
    return listOfDf

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # graph parameters
    parser.add_argument("--server", action='store_true', help="start the server")
    parser.add_argument("--import_db", default='', type=str, help="Import the files to server")
    parser.add_argument("--batch_size", default=100, type=int, help="Export batch size")
    parser.add_argument("--schedule_interval", default=10, type=int, help="schedule interval minutes")
    parser.add_argument("--save_folder", default='amt_annotated_data', type=str, help="data location")
    args = parser.parse_args()

    if len(args.import_db) > 0:
        import_job()
    if args.server:
        export_job(args.save_folder, batch_size=args.batch_size)
        info_job()
        #backup_job()
        print("Scheduling jobs...")
        schedule.every(args.schedule_interval).minutes.do(export_job, args.save_folder, batch_size=args.batch_size)
        schedule.every(args.schedule_interval).minutes.do(info_job)
        # redundant backups
        schedule.every().day.at("23:00").do(backup_job)

        while True:
            schedule.run_pending()
            time.sleep(1)
