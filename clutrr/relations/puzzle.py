"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

# Main Puzzle class which maintains the state of a single puzzle
import uuid
import random
from clutrr.utils.utils import comb_indexes
from clutrr.relations.templator import Templator
import copy
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

class Fact:
    """
    Fact class to store the additional facts
    """
    def __init__(self,
                 fact_type=None,
                 fact_edges=None):
        """

        :param fact_type: Type of the fact, supporting / irrelevant / disconnected
        :param fact_edges:
        """
        self.fact_type = fact_type
        self.fact_edges = fact_edges

    def __str__(self):
        if self.fact_edges:
            return "Type: {}, E: {}".format(self.fact_type, self.fact_edges)


class Puzzle:
    """
    Puzzle class containing the logic to build and maintain the state of a single puzzle
    """
    def __init__(self,
                 id = None,
                 target_edge=None,
                 story=None,
                 proof=None,
                 query_edge=None,
                 ancestry=None,
                 relations_obj=None
                 ):
        """

        :param id: unique id of the puzzle
        :param target_edge: the target edge, (node_a, node_b)
        :param story: list of edges consisting of the story
        :param proof: proof state of the resolution from target edge to story
        :param query_edge: edge to query, usually the same as target_edge
        :param ancestry: full background graph the story was derived from
        :param relations_obj: store of the rule base of the relations
        """
        if id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id
        self.target_edge = target_edge
        self.story = story
        self.proof_trace = proof
        self.facts = []
        self.query_edge = query_edge
        self.anc = ancestry
        self.relations_obj = relations_obj

        # derived values
        self.query_text = None
        self.target_edge_rel = None
        self.story_rel = None
        self.text_question = None
        self.relation_comb = None

        # derived full text story
        self.full_text_story = None
        # story edges with sorted node ids
        self.story_sorted_ids = None
        self.story_sort_dict = {} # mapping between the original node id and sorted node id
        # the templator instances to use
        self.train_templates = None
        self.test_templates = None

    def derive_vals(self):
        self.query_text = self.format_edge(self.target_edge)
        self.target_edge_rel = self.get_edge_relation(self.target_edge)
        self.story_rel = [self.format_edge_rel(story) for story in self.story]
        self.relation_comb =  '-'.join([self.get_edge_rel(x)['rel'] for x in self.story])

    def add_fact(self, fact_type, fact):
        """
        Add a fact to the model
        :param fact_type:
        :param fact:
        :return:
        """
        self.facts.append(Fact(fact_type=fact_type, fact_edges=fact))

    def clear_facts(self):
        """
        Clear all noise facts of the puzzle
        :return:
        """
        self.facts = []

    def get_full_story(self, randomize=True):
        """
        Combine story and facts
        :param randomize:
        :return:
        """
        full_story = self.story + [edge for fact in self.facts for edge in fact.fact_edges]
        if randomize:
            full_story = random.sample(full_story, len(full_story))
        return full_story

    def get_all_noise(self):
        """
        Get only noise edges
        :return:
        """
        return [edge for fact in self.facts for edge in fact.fact_edges]

    def get_clean_story(self):
        """
        Return the clean story
        :return:
        """
        return self.story

    def generate_text(self, stype='story', combination_length=1, templator:Templator=None, edges=None):
        """

        :param stype: can be story or fact
        :param combination_length: the max length of combining the edges for text replacement
        :param templator: templator class
        :param edges: if provided, use these edges instead of stypes
        :return:
        """
        generated_rows = []
        if edges is None:
            if stype == 'story':
                edges_to_convert = copy.copy(self.story)
            elif stype == 'fact':
                edges_to_convert = copy.copy([fact.fact_edges for fact in self.facts])
                edges_to_convert = [y for x in edges_to_convert for y in x]
            elif stype == 'target':
                edges_to_convert = [copy.copy(self.target_edge)]
            else:
                raise NotImplementedError("stype not implemented")
        else:
            edges_to_convert = edges

        combined_edges = comb_indexes(edges_to_convert, combination_length)
        for comb_group in combined_edges:
            r_combs = ['-'.join([self.get_edge_relation(edge) for edge in edge_group])
                       for edge_group in comb_group]
            # typo unfix for "neice niece"
            r_combs = [r.replace('niece','neice') if 'niece' in r else r for r in r_combs ]
            r_entities = [[ent for edge in edge_group for ent in edge] for edge_group
                          in comb_group]
            prows = [templator.replace_template(edge_group, r_entities[group_id])
                     for group_id, edge_group in enumerate(r_combs)]
            # if contains None, then reject this combination
            prc = [x for x in prows if x is not None]
            if len(prc) == len(prows):
                generated_rows.append(prows)


        # select the generated row such that the priority of
        # complex decomposition is higher. sort by length and choose the min
        generated_rows = list(sorted(generated_rows, key=len))
        generated_rows = [g for g in generated_rows if len(g) > 0]
        if stype == 'story':
            if len(generated_rows) == 0:
                # assert
                raise AssertionError()
        if len(generated_rows) > 0:
            generated_row = random.choice(generated_rows)
            for g in generated_row:
                if type(g) != str:
                    import ipdb; ipdb.set_trace()

            return generated_row
        else:
            return []

    def convert_node_ids(self, stype='story'):
        """
        Given node ids in edges, change the ids into a sorted version
        :param stype:
        :return:
        """
        if stype == 'story':
            edges_tc = copy.copy(self.story)
        elif stype == 'fact':
            edges_tc = copy.copy([fact.fact_edges for fact in self.facts])
            edges_tc = [y for x in edges_tc for y in x]
        else:
            raise NotImplementedError("stype not implemented")
        node_ct = len(self.story_sort_dict)
        for key in edges_tc:
            if key[0] not in self.story_sort_dict:
                self.story_sort_dict[key[0]] = node_ct
                node_ct += 1
            if key[1] not in self.story_sort_dict:
                self.story_sort_dict[key[1]] = node_ct
                node_ct += 1

    def get_name_gender_string(self):
        """
        Create a combination of name:Gender
        :return:
        """
        if self.story_sorted_ids is None:
            self.convert_node_ids('story')
        return ','.join(['{}:{}'.format(self.anc.family_data[node_id].name,
                                               self.anc.family_data[node_id].gender)
                                for node_id in self.story_sort_dict.keys()])

    def get_sorted_story_edges(self, stype='story'):
        """
        Overlay changed node ids onto story edges
        :param stype:
        :return:
        """
        if stype == 'story':
            edges_tc = copy.copy(self.story)
        elif stype == 'fact':
            edges_tc = copy.copy([fact.fact_edges for fact in self.facts])
            edges_tc = [y for x in edges_tc for y in x]
        else:
            raise NotImplementedError("stype not implemented")
        edge_keys_changed_id = [(self.story_sort_dict[key[0]],
                                 self.story_sort_dict[key[1]]) for key in edges_tc]
        return edge_keys_changed_id

    def get_story_relations(self, stype='story'):
        if stype == 'story':
            edges_tc = copy.copy(self.story)
        elif stype == 'fact':
            edges_tc = copy.copy([fact.fact_edges for fact in self.facts])
            edges_tc = [y for x in edges_tc for y in x]
        else:
            raise NotImplementedError("stype not implemented")
        return [self.get_edge_relation(p) for p in edges_tc]


    def get_sorted_query_edge(self):
        """
        Overlay changed node ids onto query edge
        :return:
        """
        return (self.story_sort_dict[self.target_edge[0]],
                self.story_sort_dict[self.target_edge[1]])

    def get_target_relation(self):
        """
        Get target relation
        :return:
        """
        return self.get_edge_relation(self.target_edge)

    def get_edge_rel(self, edge, rel_type='family'):
        # get node attributes
        node_b_attr = self.anc.family_data[edge[1]]
        relation = self.anc.family[edge][rel_type]
        edge_rel = self.relations_obj[relation][node_b_attr.gender]
        return edge_rel

    def get_edge_relation(self, edge, rel_type='family'):
        node_b_attr = self.anc.family_data[edge[1]]
        relation = self.anc.family[edge][rel_type]
        edge_rel = self.relations_obj[relation][node_b_attr.gender]
        return edge_rel['rel']

    def format_edge(self, edge):
        """
        Given an edge (x,y), format it into (name(x), name(y))
        :param edge:
        :return:
        """
        node_a_attr = self.anc.family_data[edge[0]]
        node_b_attr = self.anc.family_data[edge[1]]
        new_edge = (node_a_attr.name, node_b_attr.name)
        return new_edge

    def format_edge_rel(self, edge, rel_type='family'):
        """
        Given an edge (x,y), format it into (name(x), rel(x,y), name(y))
        :param edge:
        :return:
        """
        node_a_attr = self.anc.family_data[edge[0]]
        node_b_attr = self.anc.family_data[edge[1]]
        edge_rel = self.get_edge_rel(edge, rel_type)['rel']
        new_edge = (node_a_attr.name, edge_rel, node_b_attr.name)
        return new_edge

    def get_unique_relations(self):
        """
        Get all unique relations from rule store
        :return:
        """
        rels = []
        for meta_rel, val in self.relations_obj.items():
            for sp_rel, sp_val in val.items():
                rels.append(sp_val['rel'])
        rels.remove('no-relation')
        return rels

    def display(self):
        """
        Display the puzzle in a network diagram
        :return:
        """
        G = nx.MultiDiGraph()
        fs = self.get_full_story()
        names = {}
        rels = {}
        forward_edges = []
        backward_edges = []
        gendered_nodes = {'male':[], 'female':[]}
        for edge in fs:
            G.add_node(edge[0])
            G.add_node(edge[1])
            gendered_nodes[self.anc.family_data[edge[0]].gender].append(edge[0])
            gendered_nodes[self.anc.family_data[edge[1]].gender].append(edge[1])
            names[edge[0]] = self.anc.family_data[edge[0]].name
            names[edge[1]] = self.anc.family_data[edge[1]].name
            G.add_edge(edge[0], edge[1])
            forward_edges.append(edge)
            rels[edge] = self.get_edge_relation(edge)
            G.add_edge(edge[1], edge[0])
            backward_edges.append(edge)
            rels[(edge[1], edge[0])] = self.get_edge_relation((edge[1], edge[0]))
        pos = nx.layout.random_layout(G)
        nx.draw_networkx_nodes(G, pos, nodelist=gendered_nodes['male'], node_color='b', node_size=100, alpha=0.8)
        nx.draw_networkx_nodes(G, pos, nodelist=gendered_nodes['female'], node_color='r', node_size=100, alpha=0.8)
        nx.draw_networkx_labels(G, pos, names)
        nx.draw_networkx_edges(G, pos, edgelist=forward_edges, arrowstyle='-', edge_color='r')
        nx.draw_networkx_edges(G, pos, edgelist=backward_edges, arrowstyle='-', edge_color='b')
        edge_labels = nx.draw_networkx_edge_labels(G, pos, rels)
        ax = plt.gca()
        ax.set_axis_off()
        plt.show()

    def __str__(self):
        tmp = "Story : \n"
        tmp += "{} \n".format(self.story)
        tmp += "{} \n".format([self.format_edge_rel(e) for e in self.story])
        tmp += "Additional facts : \n"
        for fact in self.facts:
            tmp += "{} \n".format(fact)
        return tmp



