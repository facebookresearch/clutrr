"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

# New builder class which makes use of our new data generation

import random
import itertools as it
import copy
from clutrr.store.store import Store
import uuid
from clutrr.relations.puzzle import Puzzle


class RelationBuilder:
    """
    Relation builder class

    Steps:
    - Accept a skeleton class
    - Iteratively:
        - Invert the relations
        - Sample edge e (n1, n2)
        - Select the rule which matches this edge e (n1,n2) -> r
        - introduce a variable x so that (n1,x) + (x,n2) -> r
        - find the x which satifies both s.t x =/= {n1, n2}
        - either add to story
        - or recurse

    Changes:
        - Relation types are "family","work", etc (as given in ``relation_types``
        - When applying the rules, make sure to confirm to these types
    """

    def __init__(self,args, store:Store, anc):
        self.anc = anc
        self.args = args
        self.rules = store.rules_store
        self.store = store
        self.comp_rules = self.rules['compositional']
        self.inv_rules = self.rules['inverse-equivalence']
        self.sym_rules = self.rules['symmetric']
        self.eq_rules = self.rules['equivalence']
        self.relation_types = self.rules['relation_types']
        self.comp_rules_inv = self._invert_rule(self.rules['compositional'])
        self.inv_rules_inv = self._invert_rule(self.rules['inverse-equivalence'])
        self.sym_rules_inv = self._invert_rule(self.rules['symmetric'])
        self.eq_rules_inv = self._invert_rule(self.rules['equivalence'])
        self.relations_obj = store.relations_store
        self.boundary = args.boundary
        self.num_rel = args.relation_length
        self.puzzles = {}
        self.puzzle_ct = 0
        self.expansions = {} # (a,b) : [list]
        # save the edges which are used already
        self.done_edges = set()
        self.apply_almost_complete()
        self.precompute_expansions(list(self.anc.family.keys()))

    def _invert_rule(self, rule):
        """
        Given a rule, invert it to be RHS:LHS
        :param rule:
        :return:
        """
        inv_rules = {}
        for tp, rules in rule.items():
            inv_rules[tp] = {}
            for key, val in rules.items():
                if type(val) == str:
                    if val not in inv_rules[tp]:
                        inv_rules[tp][val] = []
                    inv_rules[tp][val].append(key)
                else:
                    for k2, v2 in val.items():
                        if v2 not in inv_rules[tp]:
                            inv_rules[tp][v2] = []
                        inv_rules[tp][v2].append((key, k2))
        return inv_rules

    def invert_rel(self, rel_type='family'):
        """
        Invert the relations
        :return:
        """
        if rel_type not in self.inv_rules:
            return None
        inv_family = copy.deepcopy(self.anc.family)
        for edge, rel in self.anc.family.items():
            relation = rel[rel_type]
            if relation in self.inv_rules[rel_type]:
                inv_rel = self.inv_rules[rel_type][relation]
                if (edge[1], edge[0]) not in inv_family:
                    inv_family[(edge[1], edge[0])] = {}
                inv_family[(edge[1], edge[0])][rel_type] = inv_rel
        self.anc.family = inv_family

    def equivalence_rel(self, rel_type='family'):
        """
        Use equivalence relations
        :return:
        """
        if rel_type not in self.eq_rules:
            return None
        n_family = copy.deepcopy(self.anc.family)
        for edge, rel in self.anc.family.items():
            relation = rel[rel_type]
            if relation in self.eq_rules[rel_type]:
                eq_rel = self.eq_rules[rel_type][relation]
                n_family[(edge[0],edge[1])][rel_type] = eq_rel
        self.anc.family = n_family

    def symmetry_rel(self, rel_type='family'):
        """
        Use equivalence relations
        :return:
        """
        if rel_type not in self.sym_rules:
            return None
        n_family = copy.deepcopy(self.anc.family)
        for edge, rel in self.anc.family.items():
            relation = rel[rel_type]
            if relation in self.sym_rules[rel_type]:
                sym_rel = self.sym_rules[rel_type][relation]
                if (edge[1], edge[0]) not in n_family:
                    n_family[(edge[1], edge[0])] = {}
                n_family[(edge[1], edge[0])][rel_type] = sym_rel
        self.anc.family = n_family


    def compose_rel(self, edge_1, edge_2, rel_type='family', verbose=False):
        """
        Given an edge pair, add the edges into a single edge following the rules
        in the dictionary
        :param edge_1: (x,z)
        :param edge_2: (z,y)
        :param rel_type:
        :return: (x,y)
        """
        # dont allow self edges
        if edge_1[0] == edge_1[1]:
            return None
        if edge_2[0] == edge_2[1]:
            return None
        if edge_1[1] == edge_2[0] and edge_1[0] != edge_2[1]:
            n_edge = (edge_1[0], edge_2[1])
            if n_edge not in self.anc.family and \
                    (edge_1 in self.anc.family and
                     self.anc.family[edge_1][rel_type] in self.comp_rules[rel_type]):
                if edge_2 in self.anc.family and \
                        self.anc.family[edge_2][rel_type] in self.comp_rules[rel_type][self.anc.family[edge_1][rel_type]]:
                    n_rel = self.comp_rules[rel_type][self.anc.family[edge_1][rel_type]][self.anc.family[edge_2][rel_type]]
                    if n_edge not in self.anc.family:
                        self.anc.family[n_edge] = {}
                    self.anc.family[n_edge][rel_type] = n_rel
                    if verbose:
                        print(edge_1, edge_2, n_rel)
                    return n_edge
        return None

    def almost_complete(self,edge):
        """
        Build an almost complete graph by iteratively applying the rules
        Recursively apply rules and invert
        :return:
        """
        # apply symmetric, equivalence and inverse rules
        self.invert_rel()
        self.equivalence_rel()
        self.symmetry_rel()
        # apply compositional rules
        keys = list(self.anc.family.keys())
        edge_1 = [self.compose_rel(e, edge) for e in keys if e[1] == edge[0]]
        edge_2 = [self.compose_rel(edge, e) for e in keys if e[0] == edge[1]]
        edge_1 = list(filter(None.__ne__, edge_1))
        edge_2 = list(filter(None.__ne__, edge_2))
        for e in edge_1:
            self.almost_complete(e)
        for e in edge_2:
            self.almost_complete(e)

    def apply_almost_complete(self):
        """
        For each edge apply ``almost_complete``
        :return:
        """
        print("Almost completing the family graph with {} nodes...".format(len(self.anc.family_data)))
        for i in range(len(self.anc.family_data)):
            for j in range(len(self.anc.family_data)):
                if i != j:
                    self.almost_complete((i, j))
        print("Initial family tree created with {} edges".format(
            len(set([k for k, v in self.anc.family.items()]))))

    def build(self):
        """
        Build the stories and targets for the current family configuration
        and save it in memory. These will be used later for post-processing
        :param num_rel:
        :return:
        """
        available_edges = set([k for k, v in self.anc.family.items()]) - self.done_edges
        #print("Available edges to derive backwards - {}".format(len(available_edges)))
        for edge in available_edges:
            pz = self.build_one_puzzle(edge)
            if pz:
                self.puzzles[pz.id] = pz
                self.puzzle_ct += 1
        if len(self.puzzles) == 0:
            print("No puzzles could be generated with this current set of arguments. Consider increasing the family tree.")
            return False
        #print("Generated {}".format(len(self.puzzles)))
        return True

    def build_one_puzzle(self, edge):
        """
        Build one puzzle
        Return False if unable to make the puzzle
        :return: type Puzzle
        """
        story, proof_trace = self.derive([edge], k=self.num_rel - 1)
        if len(story) == self.num_rel:
            id = str(uuid.uuid4())
            pz = Puzzle(id=id, target_edge=edge, story=story,
                        proof=proof_trace, ancestry=copy.deepcopy(self.anc),
                        relations_obj=copy.deepcopy(self.relations_obj))
            pz.derive_vals()
            return pz
        else:
            return False


    def reset_puzzle(self):
        """Reset puzzle to none"""
        self.puzzles = {}
        self.puzzles_ct = 0

    def unique_patterns(self):
        """Get unique patterns in this puzzle"""
        f_comb_count = {}
        for pid, puzzle in self.puzzles.items():
            if puzzle.relation_comb not in f_comb_count:
                f_comb_count[puzzle.relation_comb] = 0
            f_comb_count[puzzle.relation_comb] += 1
        return set(f_comb_count.keys())


    def _value_counts(self):
        pztype = {}
        for pid, puzzle in self.puzzles.items():
            f_comb = puzzle.relation_comb
            if f_comb not in pztype:
                pztype[f_comb] = []
            pztype[f_comb].append(pid)
        return pztype

    def prune_puzzles(self, weight=None):
        """
        In order to keep all puzzles homogenously distributed ("f_comb"), we calcuate
        the count of all type of puzzles, and retain the minimum count
        :param weight: a dict of weights f_comb:p where 0 <= p <= 1
        :return:
        """
        pztype = self._value_counts()
        pztype_min_count = min([len(v) for k,v in pztype.items()])
        keep_puzzles = []
        for f_comb, pids in pztype.items():
            keep_puzzles.extend(random.sample(pids, pztype_min_count))
        not_keep = set(self.puzzles.keys()) - set(keep_puzzles)
        for pid in not_keep:
            del self.puzzles[pid]
        if weight:
            pztype = self._value_counts()
            # fill in missing weights
            for f_comb, pids in pztype.items():
                if f_comb not in weight:
                    weight[f_comb] = 1.0
            keep_puzzles = []
            for f_comb,pids in pztype.items():
                if weight[f_comb] == 1.0:
                    keep_puzzles.extend(pids)
            not_keep = set(self.puzzles.keys()) - set(keep_puzzles)
            for pid in not_keep:
                del self.puzzles[pid]


    def add_facts_to_puzzle(self, puzzle):
        """
            For a given puzzle, add different types of facts
                - 1 : Provide supporting facts. After creating the essential fact graph, expand on any
                k number of edges (randomly)
                - 2: Irrelevant facts: after creating the relevant fact graph, expand on an edge,
                 but only provide dangling expansions
                - 3: Disconnected facts: along with relevant facts, provide a tree which is completely
                separate from the proof path
                - 4: Random attributes: school, place of birth, etc.
            If unable to add the required facts, return False
            Else, return the puzzle
        :return:
        """
        if self.args.noise_support:
            # Supporting facts
            # A <-> B <-> C ==> A <-> D <-> C , A <-> D <-> B <-> C
            story = puzzle.story
            extra_story = []
            for se in story:
                e_pair = self.expand_new(se)
                if e_pair:
                    if puzzle.target_edge not in e_pair and e_pair[0][1] not in set([p for e in puzzle.story for p in e]):
                        extra_story.append(tuple(e_pair))
            if len(extra_story) == 0:
                return False
            else:
                # choose a sample of 1 to k-1 edge pairs
                num_edges = random.choice(range(1, (len(story) // 2) + 1))
                extra_story = random.sample(extra_story, min(num_edges, len(extra_story)))
                # untuple the extra stories
                extra_story = [k for e in extra_story for k in e]
                self._test_supporting(story, extra_story)
            puzzle.add_fact(fact_type='supporting', fact=extra_story)
        if self.args.noise_irrelevant:
            # Irrelevant facts
            # A <-> B <-> C ==> A <-> D <-> E
            # Must have only one common node with the story
            story = puzzle.story
            num_edges = len(story)
            sampled_edge = random.choice(story)
            extra_story = []
            for i in range(num_edges):
                tmp = sampled_edge
                seen_pairs = set()
                pair = self.expand_new(sampled_edge)
                if pair:
                    while len(extra_story) == 0 and (tuple(pair) not in seen_pairs):
                        seen_pairs.add(tuple(pair))
                        for e in pair:
                            if e != puzzle.target_edge and not self._subset(story, [e], k=2):
                                extra_story.append(e)
                                sampled_edge = e
                                break
                    if tmp == sampled_edge:
                        sampled_edge = random.choice(story)
            if len(extra_story) == 0:
                return False
            else:
                # add a length restriction so as to not create super long text
                # length restriction should be k+1 than the current k
                extra_story = random.sample(extra_story, min(len(extra_story), len(story) // 2))
                self._test_irrelevant(story, extra_story)
                puzzle.add_fact(fact_type='irrelevant', fact=extra_story)
        if self.args.noise_disconnected:
            # Disconnected facts
            story = puzzle.story
            nodes_story = set([y for x in list(story) for y in x])
            nodes_not_in_story = set(self.anc.family_data.keys()) - nodes_story
            possible_edges = [(x, y) for x, y in it.combinations(list(nodes_not_in_story), 2) if
                              (x, y) in self.anc.family]
            num_edges = random.choice(range(1, (len(story) // 2) + 1))
            possible_edges = random.sample(possible_edges, min(num_edges, len(possible_edges)))
            if len(possible_edges) == 0:
                return False
            self._test_disconnected(story, possible_edges)
            puzzle.add_fact(fact_type='disconnected', fact=possible_edges)
        return puzzle

    def add_facts(self):
        """
            For a given puzzle, add different types of facts
                - 1 : Provide supporting facts. After creating the essential fact graph, expand on any
                k number of edges (randomly)
                - 2: Irrelevant facts: after creating the relevant fact graph, expand on an edge,
                 but only provide dangling expansions
                - 3: Disconnected facts: along with relevant facts, provide a tree which is completely
                separate from the proof path
                - 4: Random attributes: school, place of birth, etc.
            If unable to add the required facts, return False
        :return:
        """
        mark_ids_for_deletion = []
        for puzzle_id in self.puzzles.keys():
            puzzle = self.add_facts_to_puzzle(self.puzzles[puzzle_id])
            if puzzle:
                self.puzzles[puzzle_id] = puzzle
            else:
                mark_ids_for_deletion.append(puzzle_id)
        for id in mark_ids_for_deletion:
            del self.puzzles[id]


    def precompute_expansions(self, edge_list, tp='family'):
        """
        Given a list of edges, precompute the one level expansions on all of them
        Given (x,y) -> get (x,z), (z,y) s.t. it follows our set of rules
        Store the expansions as a list : (x,y) : [[(x,a),(a,y)], [(x,b),(b,y)] ... ]
        :param edge_list:
        :return:
        """
        for edge in edge_list:
            relation = self.anc.family[edge][tp]
            if relation not in self.comp_rules_inv[tp]:
                continue
            rules = list(self.comp_rules_inv[tp][relation])
            for rule in rules:
                for node in self.anc.family_data.keys():
                    e1 = (edge[0], node)
                    e2 = (node, edge[1])
                    if e1 in self.anc.family and self.anc.family[e1][tp] == rule[0] \
                            and e2 in self.anc.family and self.anc.family[e2][tp] == rule[1]:
                        new_edge_pair = [e1, e2]
                        if edge not in self.expansions:
                            self.expansions[edge] = []
                        self.expansions[edge].append(new_edge_pair)
            self.expansions[edge] = it.cycle(self.expansions[edge])

    def expand_new(self, edge, tp='family'):
        relation = self.anc.family[edge][tp]
        if relation not in self.comp_rules_inv[tp]:
            return None
        if edge in self.expansions:
            return self.expansions[edge].__next__()
        else:
            return None

    def expand(self, edge, tp='family'):
        """
        Given an edge, break the edge into two compositional edges from the given
        family graph. Eg, if input is (x,y), break the edge into (x,z) and (z,y)
        following the rules
        :param edge: Edge to break
        :param ignore_edges: Edges to ignore while breaking an edge. Used to ignore loops
        :param k: if k == 0, stop recursing
        :return:
        """
        relation = self.anc.family[edge][tp]
        if relation not in self.comp_rules_inv[tp]:
            return None
        rules = list(self.comp_rules_inv[tp][relation])
        while len(rules) > 0:
            rule = random.choice(rules)
            rules.remove(rule)
            for node in self.anc.family_data.keys():
                e1 = (edge[0], node)
                e2 = (node, edge[1])
                if e1 in self.anc.family and self.anc.family[e1][tp] == rule[0] \
                        and e2 in self.anc.family and self.anc.family[e2][tp] == rule[1]:
                    return [e1, e2]
        return None

    def derive(self, edge_list, k=3):
        """
        Given a list of edges, expand elements from the edge until we reach k
        :param edge_list:
        :param k:
        :return:
        """
        proof_trace = []
        seen = set()
        while k>0:
            if len(set(edge_list)) - len(seen) == 0:
                break
            if len(list(set(edge_list) - seen)) == 0:
                break
            e = random.choice(list(set(edge_list) - seen))
            seen.add(e)
            ex_e = self.expand_new(e)
            if ex_e and (ex_e[0] not in seen and ex_e[1] not in seen and ex_e[0][::-1] not in seen and ex_e[1][::-1] not in seen):
                pos = edge_list.index(e)
                edge_list.insert(pos, ex_e[-1])
                edge_list.insert(pos, ex_e[0])
                edge_list.remove(e)
                #edge_list.extend(ex_e)
                # format proof into human readable form
                e = self._format_edge_rel(e)
                ex_e = [self._format_edge_rel(x) for x in ex_e]
                proof_trace.append({e:ex_e})
                k = k-1
        return edge_list, proof_trace

    def _get_edge_rel(self, edge, rel_type='family'):
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

    def _format_edge(self, edge):
        """
        Given an edge (x,y), format it into (name(x), name(y))
        :param edge:
        :return:
        """
        node_a_attr = self.anc.family_data[edge[0]]
        node_b_attr = self.anc.family_data[edge[1]]
        new_edge = (node_a_attr.name, node_b_attr.name)
        return new_edge

    def _format_edge_rel(self, edge, rel_type='family'):
        """
        Given an edge (x,y), format it into (name(x), rel(x,y), name(y))
        :param edge:
        :return:
        """
        node_a_attr = self.anc.family_data[edge[0]]
        node_b_attr = self.anc.family_data[edge[1]]
        edge_rel = self._get_edge_rel(edge, rel_type)['rel']
        new_edge = (node_a_attr.name, edge_rel, node_b_attr.name)
        return new_edge

    def stringify(self, edge, rel_type='family'):
        """
        Build story string from the edge
        :param edge: tuple
        :return:
        """
        # get node attributes
        node_a_attr = self.anc.family_data[edge[0]]
        node_b_attr = self.anc.family_data[edge[1]]
        relation = self._get_edge_rel(edge, rel_type)
        placeholders = relation['p']
        placeholder = random.choice(placeholders)
        node_a_name = node_a_attr.name
        node_b_name = node_b_attr.name
        assert node_a_name != node_b_name
        if self.boundary:
            node_a_name = '[{}]'.format(node_a_name)
            node_b_name = '[{}]'.format(node_b_name)
        text = placeholder.replace('e_1', node_a_name)
        text = text.replace('e_2', node_b_name)
        return text + '. '

    def generate_puzzles(self, weight=None):
        """
        Prune the puzzles according to weight
        Deprecated: puzzle generation logic moved to `build`
        :return:
        """
        self.prune_puzzles(weight)


    def generate_question(self, query):
        """
        Given a query edge, generate a textual question from the question placeholder bank
        Use args.question to either generate a relational question or a yes/no question
        :param query:
        :return:
        """
        # TODO: return a question from the placeholder
        # TODO: future work
        return ''

    def _flatten_tuples(self, story):
        return list(sum(story, ()))

    def _unique_nodes(self, story):
        return set(self._flatten_tuples(story))

    def _subset(self, story, fact, k=2):
        """
        Whether at least k fact nodes are present in a given story
        :param story:
        :param fact:
        :return:
        """
        all_entities = self._unique_nodes(story)
        all_fact_entities = self._unique_nodes(fact)
        return len(all_entities.intersection(all_fact_entities)) >= k

    ## Testing modules

    def _test_story(self, story):
        """
        Given a list of edges of the story, test whether they are logically valid
        (x,y),(y,z) is valid, (x,y),(x,z) is not
        :param story: list of tuples
        :return:
        """
        for e_i in range(len(story) - 1):
            assert story[e_i][-1] == story[e_i + 1][0]


    def _test_disconnected(self, story, fact):
        """
        Given a story and the fact, check whether the fact is a disconnected fact
        If irrelevant, then there would be no node match between story and fact
        :param story: Array of tuples
        :param fact: Array of tuples
        :return:
        """
        all_entities = self._unique_nodes(story)
        all_fact_entities = self._unique_nodes(fact)
        assert len(all_entities.intersection(all_fact_entities)) == 0

    def _test_irrelevant(self, story, fact):
        """
        Given a story and the fact, check whether the fact is a irrelevant fact
        If irrelevant, then there would be exactly one node match between story and fact
        :param story: Array of tuples
        :param fact: Array of tuples
        :return:
        """
        all_entities = self._unique_nodes(story)
        all_fact_entities = self._unique_nodes(fact)
        assert len(all_entities.intersection(all_fact_entities)) == 1

    def _test_supporting(self, story, fact):
        """
        Given a story and the fact, check whether the fact is a irrelevant fact
        If irrelevant, then there would be >= 2 node match between story and fact
        :param story: Array of tuples
        :param fact: Array of tuples
        :return:
        """
        all_entities = self._unique_nodes(story)
        all_fact_entities =self._unique_nodes(fact)
        assert len(all_entities.intersection(all_fact_entities)) >= 2





