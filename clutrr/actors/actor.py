"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

import random

class Actor:
    """
    male or female actor

    """
    def __init__(self, gender='male', name='', node_id=0, store={}):
        self.gender = gender
        self.name = name
        self.node_id = node_id
        ## irrelevant attributes
        ## also make the irrelevant attributes random. Not every entity will have them all
        self.attributes = {
            'school'    : '',
            'location_born' : '',
            'social_media_active' : False,
            'social_media_preferred': '',
            'political_views' : '',
            'hobby' : '',
            'sport': '',
        }
        self.attribute_store = store.attribute_store
        self.fill_attributes()

    def fill_attributes(self):
        for key,val in self.attribute_store.items():
            random_val = random.choice(val['options'])
            random_attr = '[{}]'.format(random_val)
            name = '[{}]'.format(self.name)
            random_placeholder = random.choice(val['placeholders'])
            text = random_placeholder.replace('e_x', name).replace('attr_x', random_attr) + ". "
            self.attributes[key] = text

    def __repr__(self):
        return "<Actor name:{} gender:{} node_id:{}".format(
            self.name, self.gender, self.node_id)

    def __str__(self):
        return "Actor node, name: {}, gender : {}, node_id : {}".format(
            self.name, self.gender, self.node_id
        )

class Entity:
    """
    work or related entities
    etype="work"

    """
    def __init__(self, name='', etype='', node_id=0):
        self.name = name
        self.etype = etype
        self.node_id = node_id

    def __repr__(self):
        return "<Entity name:{} etype: {} node_id:{}".format(
            self.name, self.etype, self.node_id)

    def __str__(self):
        return "Entity node, name: {}, etype: {}, node_id : {}".format(
            self.name, self.etype, self.node_id
        )




























