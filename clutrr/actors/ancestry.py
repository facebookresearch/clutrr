"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

import numpy as np
import names
import copy
import random
from clutrr.actors.actor import Actor, Entity
from clutrr.store.store import Store

#store = Store()

class Ancestry:
    """
    Ancestry of people to simulate

    Class to create a skeleton graph

    Changes:

    - Maintain a dictionary instead of networkx graph.
    - The keys to the dictionary will be (node_id_x, node_id_y) : a dict of relations
        - a dict of relations will ensure the use of family, work, etc different relations logically seperate
        - key of the relations:
            - "family" --> family type relations
            - "work"   --> work related relations
    - Maintain a separate dictionary for mapping of node_id to details
    - Relation keyword to be taken from rules_store
    """
    def __init__(self, args, store:Store,
                 relationship_type={'SO':1,'child':2}, taken_names=None):
        self.family = {} # dict (node_id_a, node_id_b) : rel dict
        self.family_data = {} # dict to hold node_id details
        self.work_data = {} # dict to hold work location id details
        self.store = store
        self.max_levels = args.max_levels
        self.min_child = args.min_child
        self.max_child = args.max_child
        self.p_marry = args.p_marry
        self.relationship_type = relationship_type
        self.levels = 0 # keep track of the levels
        self.node_ct = 0
        self.flipped = [] # track of nodes which are gender flipped
        self.taken_names = taken_names if taken_names else copy.deepcopy(self.store.attr_names) # keep track of names which are already taken
        self.simulate()
        #self.add_work_relations()

    def simulate(self):
        """
        Main function to run the simulation to create a family tree

        :return:
        """
        self.node_ct = 0
        self.levels = random.randint(1,self.max_levels)
        # we are root, for now just add one head of family
        gender = 'male'
        nodes = self.add_members(gender=gender, num=1)
        parents = nodes

        for level in range(self.max_levels):
            # build generation
            generation_nodes = []
            for node in parents:
                # marry with probability p_marry
                decision_marry = np.random.choice([True,False],1,p=[self.p_marry, 1-self.p_marry])
                if decision_marry:
                    # add the partner
                    nodes =  self.add_members(gender=self.toggle_gender(node), num=1)
                    self.make_relation(node, nodes[0], relation='SO')
                    # always leave the last level as single children
                    if level != self.max_levels - 1:
                        # add the children for this parent
                        num_childs = random.randint(self.min_child, self.max_child)
                        child_nodes = self.add_members(num=num_childs)
                        if len(child_nodes) > 0:
                            for ch_node in child_nodes:
                                self.make_relation(node, ch_node, relation='child')
                                self.make_relation(nodes[0], ch_node, relation='child')
                        generation_nodes.extend(child_nodes)
            parents = generation_nodes



    def add_members(self, gender='male', num=1):
        """
        Add members into family
        :param gender: male/female. if num > 1 then randomize
        :param num: default 1.
        :return: list of node ids added, new node id
        """
        node_id = self.node_ct
        added_nodes = []
        for x in range(num):
            if num > 1:
                gender = random.choice(['male', 'female'])
            # select a name that is not taken
            name = names.get_first_name(gender=gender)
            while name in self.taken_names:
                name = names.get_first_name(gender=gender)
            self.taken_names.add(name)
            node = Actor(
                name=name, gender=gender, node_id=node_id, store=self.store)
            added_nodes.append(node)
            self.family_data[node_id] = node
            node_id += 1
        self.node_ct = node_id
        return added_nodes

    def make_relation(self, node_a, node_b, relation='SO'):
        """
        Add a relation between two nodes
        :param node_a: integer id of the node
        :param node_b: integer id of the node
        :param relation: either SO->1, or child->2
        :return:
        """
        node_a_id = node_a.node_id
        node_b_id = node_b.node_id
        rel_tuple = (node_a_id, node_b_id)
        if rel_tuple not in self.family:
            self.family[rel_tuple] = {'family': relation}

    def toggle_gender(self, node):
        if node.gender == 'male':
            return 'female'
        else:
            return 'male'

    def print_family(self):
        ps = ','.join(["{}.{}.{}".format(k, v.name[0], v.gender) for k,v in self.family_data.items()])
        return ps

    def next_flip(self):
        """
        Given an ancestry,
            - maintain a set of nodes who have already been gender flipped
            - sample one node to flip from the rest
            - check if the node contains a SO relationship. if so, toggle both
            - add the flipped nodes into the already flipped pile
            - if no nodes are left, then return False. else return True
        :return:
        """
        candidates = list(set(self.family_data.keys()) - set(self.flipped))
        if len(candidates) == 0:
            # all candidates flipped already
            # reset flip
            self.flipped = []
        else:
            node = random.choice(candidates)
            relations_with_node = [node_pair for node_pair in self.family.keys() if node_pair[0] == node]
            SO_relation = [node_pair for node_pair in relations_with_node if self.family[node_pair]['family'] == 'SO']
            assert len(SO_relation) <= 1
            if len(SO_relation) == 1:
                so_node = SO_relation[0][1]
                # flip both
                self.family_data[node].gender = self.toggle_gender(self.family_data[node])
                self.family_data[so_node].gender = self.toggle_gender(self.family_data[so_node])
                # exchange their names too
                tmp_name = self.family_data[node].name
                self.family_data[node].name = self.family_data[so_node].name
                self.family_data[so_node].name = tmp_name
                self.flipped.append(node)
                self.flipped.append(so_node)
                #print("flipping couples ...")
                #print("Flipped {} to {}".format(node, self.family_data[node].gender))
                #print("Flipped {} to {}".format(so_node, self.family_data[so_node].gender))
            else:
                # only childs, flip them
                self.family_data[node].gender = self.toggle_gender(self.family_data[node])
                # choose a new gender appropriate name
                gender = self.family_data[node].gender
                while name in self.taken_names:
                    name = names.get_first_name(gender=gender)
                self.family_data[node].name = name
                self.flipped.append(node)
                #print("flipping singles ...")
                #print("Flipped {} to {}".format(node, self.family_data[node].gender))



    def add_work_relations(self, w=0.3):
        """
        Policy of adding working relations:
        - Add w work locations
        - Divide the population into these w bins
        - Add works_at relation
        - Within each bin:
            - Assign m managers
        :return:
        """
        num_pop = len(self.family_data)
        pop_ids = self.family_data.keys()
        work_locations = random.sample(self.store.attribute_store['work']['options'], int(num_pop * w))
        node_ct = self.node_ct
        work_bins = {}
        pop_per_loc = num_pop // len(work_locations)
        for wl in work_locations:
            self.work_data[node_ct] = Entity(name=wl, etype='work')
            w = random.sample(pop_ids, pop_per_loc)
            pop_ids = list(set(pop_ids) - set(w))
            work_bins[wl] = {"id": node_ct, "w": w}
            node_ct+=1
        if len(pop_ids) > 0:
            work_bins[work_locations[-1]]["w"].extend(pop_ids)
        self.node_ct = node_ct
        for wl in work_locations:
            e_id = work_bins[wl]["id"]
            pops = work_bins[wl]["w"]
            for p in pops:
                edge = (e_id, p)
                if edge not in self.family:
                    self.family[edge] = {'family':'', 'work': []}
                if 'work' not in self.family[edge]:
                    self.family[edge]['work'] = []
                self.family[edge]['work'].append('works_at')
            # select manager
            manager = random.choice(pops)
            for p in pops:
                edge = (p, manager)
                if edge not in self.family:
                    self.family[edge] = {'family':'', 'work': []}
                if 'work' not in self.family[edge]:
                    self.family[edge]['work'] = []
                self.family[edge]['work'].append('manager')



if __name__=='__main__':
    #pdb.set_trace()
    anc = Ancestry()
    anc.add_work_relations()