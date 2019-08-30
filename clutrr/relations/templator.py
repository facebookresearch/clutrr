"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

import copy
import random

class Templator:
    """
    Templator base class
    """
    def __init__(self, templates, family):
        self.templates = copy.copy(templates)
        self.family = family # dict containing node informations
        self.used_template = ''
        self.entity_id_dict = {}
        self.seen_ent = set()

    def choose_template(self, *args, **kwargs):
        pass

    def replace_template(self, *args, **kwargs):
        pass


class TemplatorAMT(Templator):
    """
    Replaces story with the templates obtained from AMT
    """
    def __init__(self, templates, family):
        super(TemplatorAMT, self).__init__(templates=templates, family=family)

    def choose_template(self, f_comb, entities, verbose=False):
        """
        Choose a template to use. Do not use the same template in this current context
        :return:
        """
        self.entity_id_dict = {}
        self.seen_ent = set()
        gender_comb = []
        # build the dictionary of entity - ids
        for ent in entities:
            if ent not in self.seen_ent:
                gender_comb.append(self.family[ent].gender)
                self.seen_ent.add(ent)
                self.entity_id_dict[ent] = len(self.entity_id_dict)
        gender_comb = '-'.join(gender_comb)
        if verbose:
            print(f_comb)
            print(gender_comb)
            print(len(self.templates[f_comb][gender_comb]))
        if gender_comb not in self.templates[f_comb] or len(self.templates[f_comb][gender_comb]) == 0:
            raise NotImplementedError("template combination not found.")
        available_templates = self.templates[f_comb][gender_comb]
        chosen_template = random.choice(available_templates)
        self.used_template = chosen_template
        used_i = self.templates[f_comb][gender_comb].index(chosen_template)
        # remove the used template
        # del self.templates[f_comb][gender_comb][used_i]
        return chosen_template


    def replace_template(self, f_comb, entities, verbose=False):
        try:
            chosen_template = self.choose_template(f_comb, entities, verbose=verbose)

            for ent_id, ent in enumerate(list(set(entities))):
                node = self.family[ent]
                gender = node.gender
                name = node.name
                chosen_template = chosen_template.replace('ENT_{}_{}'.format(self.entity_id_dict[ent], gender), '[{}]'.format(name))
            return chosen_template
        except:
            # chosen template not found
            return None


class TemplatorSynthetic(Templator):
    """
    Replaces story with the templates obtained from Synthetic rule base
    Here, templates is self.relations_obj[relation]
    """
    def __init__(self, templates, family):
        super(TemplatorSynthetic, self).__init__(templates=templates, family=family)

    def choose_template(self, f_comb, entities, verbose=False):
        """
        Choose a template to use. Do not use the same template in this current context
        :return:
        """
        self.entity_id_dict = {}
        self.seen_ent = set()
        available_templates = self.templates[f_comb]
        chosen_template = random.choice(available_templates)
        self.used_template = chosen_template
        return chosen_template


    def replace_template(self, f_comb, entities, verbose=False):
        assert len(entities) == 2
        chosen_template = self.choose_template(f_comb, entities, verbose=verbose)

        node_a_attr = self.family[entities[0]]
        node_b_attr = self.family[entities[1]]
        node_a_name = node_a_attr.name
        node_b_name = node_b_attr.name
        assert node_a_name != node_b_name
        node_a_name = '[{}]'.format(node_a_name)
        node_b_name = '[{}]'.format(node_b_name)
        text = chosen_template.replace('e_1', node_a_name)
        text = text.replace('e_2', node_b_name)
        return text + '. '