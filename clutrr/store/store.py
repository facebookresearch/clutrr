"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

import os
import json
import yaml

class Store:
    def __init__(self,args):
        attribute_store = args.attribute_store if args.attribute_store else 'attribute_store.json'
        relations_store = args.relations_store if args.relations_store else 'relations_store.json'
        question_store = args.question_store if args.question_store else 'question_store.json'
        rules_store = args.rules_store if args.rules_store else 'rules_store.yaml'
        self.base_path = os.path.dirname(os.path.realpath(__file__)).split('store')[0]
        self.attribute_store = json.load(open(os.path.join(self.base_path, 'store', attribute_store)))
        self.relations_store = yaml.load(open(os.path.join(self.base_path, 'store', relations_store)))
        self.question_store = yaml.load(open(os.path.join(self.base_path, 'store', question_store)))
        self.rules_store = yaml.load(open(os.path.join(self.base_path, 'store', rules_store)))

        # TODO: do we need this?
        ## Relationship type has basic values 0,1 and 2, whereas the
        ## rest should be inferred. Like, child + child = 4 = grand
        self.relationship_type = {
            'SO': 1,
            'child': 2,
            'sibling': 0,
            'in-laws': 3,
            'grand': 4,
            'no-relation': -1
        }

        attr_names = [v["options"] for k,v in self.attribute_store.items()]
        self.attr_names = set([x for p in attr_names for x in p])