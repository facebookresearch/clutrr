#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
# Generator which integrates GLC
# This scripts expects the output from glc.py, whose locations should be provided in config.yaml

from typing import List, Any, Dict, Tuple
import hydra
from omegaconf import DictConfig, OmegaConf
from pathlib import Path
import numpy as np
import random
import os
import json
import pandas as pd
import yaml
import copy
from tqdm.rich import tqdm

from clutrr.utils.utils import comb_indexes
import logging
from rich.logging import RichHandler

# Disable hydra internal loggings
for _ in logging.root.manager.loggerDict:
    logging.getLogger(_).setLevel(logging.CRITICAL)

import warnings

# Ignore hydra warnings
warnings.filterwarnings("ignore")

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler()],
)

log = logging.getLogger(__name__)

from rich.console import Console

console = Console()
## Utility functions


## Utility functions


def set_seed(seed):
    """Set seed"""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


def dump_jsonl(data, output_path, append=False):
    """
    Write list of objects to a JSON lines file.
    """
    mode = "a+" if append else "w"
    with open(output_path, mode, encoding="utf-8") as f:
        for line in data:
            json_record = json.dumps(line, ensure_ascii=False)
            f.write(json_record + "\n")
    log.info("Wrote {} records to {}".format(len(data), output_path))


def load_jsonl(input_path) -> list:
    """
    Read list of objects from a JSON lines file.
    """
    data = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line.rstrip("\n|\r")))
    log.info("Loaded {} records from {}".format(len(data), input_path))
    return data


## Generator specific functions


def apply_gender(args, data_row) -> Dict[str, Any]:
    """
    - Mark gender of entities
    - Gender of second query entity determines the final target
    - Load the gender map from `gender_map`
    - Add the key `descriptor_gender` with gendered relations
    - Add the key `gender_map` to be dictionary of entity -> genders
    - Add the key `target_gender` with the correct gender target

    :return: modified data_row
    """
    gd_map = yaml.load(
        open(get_current_folder() / args.gender_map), Loader=yaml.FullLoader
    )
    entities = list(
        set([e[0] for e in data_row["edges"]] + [e[1] for e in data_row["edges"]])
    )
    # randomly assing a gender
    gender_map = {}
    for ent in entities:
        if random.uniform(0, 1) > 0.5:
            gender_map[ent] = "male"
        else:
            gender_map[ent] = "female"
    # Correct for SO
    # If SO is present, then make sure either of the genders are opposite
    # CLUTRR doesn't have any LGBTQ templates, please submit a PR to add it!
    for _, edge in enumerate(data_row["edges"]):
        if edge[-1] == "SO":
            if gender_map[edge[0]] == gender_map[edge[1]]:
                # choose which one to toggle
                random_ent = random.choice(edge[:2])
                orig_rel = gender_map[random_ent]
                if orig_rel == "male":
                    gender_map[random_ent] = "female"
                else:
                    gender_map[random_ent] = "male"

    last_entity = data_row["query"][1]
    last_entity_gender = gender_map[last_entity]
    target_gender = gd_map[data_row["target"]][last_entity_gender]["rel"]
    descriptor_gender = ",".join(
        [
            gd_map[des][gender_map[data_row["resolution_path"][di + 1]]]["rel"]
            for di, des in enumerate(data_row["descriptor"].split(","))
        ]
    )
    data_row["descriptor_gender"] = descriptor_gender
    data_row["target_gender"] = target_gender
    data_row["gender_map"] = gender_map

    return data_row


def get_current_folder():
    try:
        cur_folder = Path(hydra.utils.get_original_cwd())
    except:
        # in tests, return current path
        cur_folder = Path(".")
    return cur_folder


def get_names(args) -> Any:
    """
    Download English gendered names if file not present
    """
    cur_folder = get_current_folder()
    names_file = cur_folder / args.names_file
    if names_file.exists():
        return pd.read_csv(names_file)
    else:
        # warning: will attempt to read ~35MB from the internet
        remote_df = pd.read_csv(args.names_url)
        male_names = remote_df[remote_df.gender == "M"].iloc[0 : args.num_names]
        female_names = remote_df[remote_df.gender == "F"].iloc[0 : args.num_names]
        all_names = pd.concat([male_names, female_names])
        all_names.to_csv(names_file)
        return all_names


def assign_names(args, data_row) -> Dict[str, Any]:
    """
    - Load the list of names
    - Assing names drawn from common names list (gendered)
    - Add a key `name_map` to be dictionary of entity -> name
    - Add a key `named_edges` to be a list of edges where entities are replaced by names
    and relations are replaced according to the gender of the second entity
    """
    names = get_names(args)
    if "gender_map" not in data_row:
        raise AssertionError("run apply_gender before assigning names")
    gender_map = data_row["gender_map"]
    name_map = {}
    for ent, gender in gender_map.items():
        assigned_names = list(name_map.keys())
        if gender == "male":
            search_tag = "M"
        else:
            search_tag = "F"
        sampled_name = (
            names[(~names.name.isin(assigned_names)) & (names.gender == search_tag)]
            .sample(1)
            .iloc[0]["name"]
        )
        name_map[ent] = sampled_name
    data_row["name_map"] = name_map
    gd_map = yaml.load(
        open(get_current_folder() / args.gender_map), Loader=yaml.FullLoader
    )
    named_edges = []
    for edge in data_row["edges"]:
        er = [name_map[edge[0]], name_map[edge[1]]]
        gender_of_last = gender_map[edge[1]]
        er.append(gd_map[edge[2]][gender_of_last]["rel"])
        named_edges.append(er)
    data_row["named_edges"] = named_edges
    return data_row


def get_entity_gender_combination(data_row, edge_ids) -> Tuple[List[int], str]:
    """
    Return a string of genders for a combination of edges
    For example, if edge_ids = [1,2] then combine the entities in this order
    """
    entities = [data_row["edges"][edge_ids[0]][0]] + [
        data_row["edges"][eid][1] for eid in edge_ids
    ]
    ent_gender = "-".join([data_row["gender_map"][e] for e in entities])
    return entities, ent_gender


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def sample_combination(
    args,
    data_row,
    templates,
    debug=False,
    split="train",
) -> Tuple[List[str], List[List[int]]]:
    """
    Select the edges to combine, and then apply template on top of it
    Edges can be combined in various ways. For eg, 4 edges can be combined
    as : [1,1,1,1] (each edge on its own) to [3,1] (three edge combined, with 1 remaining)
    Function defined in `comb_indexes` in utils/utils.py

        :Return:
        - final_combination : [father, mother, son, father]
        - edge_ids_group: [[1],[2],[3],[4]]
    """
    if args.template_type == "amt":
        MAX_COMBINATION_NUMBER = 3  # CLUTRR only supports 3 for now in AMT. For more support, collect more templates!
    else:
        MAX_COMBINATION_NUMBER = 1
    templates = copy.copy(templates[split])
    edge_ids = list(range(len(data_row["edges"])))
    # To run this faster we batch the processing to chunks of 5
    batch_edge_ids = chunks(edge_ids, 5)
    final_combinations = []
    edge_ids_groups = []
    for edge_ids in batch_edge_ids:
        edge_combinations = comb_indexes(edge_ids, MAX_COMBINATION_NUMBER)
        # Convert edge combinations to - separated named relation types
        named_rel_combinations = [
            [
                "-".join([data_row["named_edges"][eid][-1] for eid in group])
                for group in comb
            ]
            for comb in edge_combinations
        ]

        # Filter combinations are available in the template
        filtered_combs = []
        for gi, group in enumerate(named_rel_combinations):
            present = True
            for comb in group:
                if comb not in templates:
                    present = False
                    break
            if present:
                filtered_combs.append((gi, group))

        ## Further, filter combinations which has the correct gender ordering
        gender_filtered_combs = []
        for gi, group in filtered_combs:
            present = True
            for ci, comb in enumerate(group):
                edge_ids = edge_combinations[gi][ci]
                _, ent_gender = get_entity_gender_combination(data_row, edge_ids)
                if ent_gender not in templates[comb]:
                    present = False
                    # TODO: It seems many gender configurations are missing from the templates
                    # log.info(f"Need {ent_gender} in {comb}")
                    break
            if present:
                gender_filtered_combs.append((gi, group))

        # log.info(f"Available combinations : {len(filtered_combs)}")
        # log.info(f"Available gender filtered combinations : {len(gender_filtered_combs)}")

        # Choose a single combination
        if len(gender_filtered_combs) > 0:
            final_combination = random.choice(gender_filtered_combs)
            gi, group = final_combination
            edge_ids_group = edge_combinations[gi]
            final_combinations.extend(final_combination[1])
            edge_ids_groups.extend(edge_ids_group)
        else:
            # log.info(filtered_combs)
            # log.info(gender_filtered_combs)
            raise AssertionError(
                "One or more templates are missing from the provided file."
            )
    return final_combinations, edge_ids_groups


def apply_template_on_edges(
    args,
    data_row,
    templates,
    separator=" ",
    name_boundary=False,
    debug=False,
    split="train",
) -> Dict[str, Any]:
    """
    Apply templates on the edges

    Parameters
    - args: Config
    - data_row: Input data row
    - templates: dictionary of templates
    - separator: Sentence separator
    - name_boundary: whether to add a "[]" boundary surrounding the names
    - debug: Inspect method
    - split: which split the templates should be chosen from (train/valid/test)


    :Return: modified data_row
    """
    data_row = apply_gender(args, data_row)
    data_row = assign_names(args, data_row)
    final_combination, edge_ids_group = sample_combination(
        args, data_row, templates, debug, split=split
    )
    story = ""
    used_templates = []
    for ci, comb in enumerate(final_combination):
        entities, gender_str = get_entity_gender_combination(
            data_row, edge_ids_group[ci]
        )
        named_entities = [data_row["name_map"][e] for e in entities]
        gender_of_entities = [data_row["gender_map"][e] for e in entities]
        chosen_template = random.choice(templates[split][comb][gender_str])
        fact = copy.deepcopy(chosen_template)
        # save used templates for posterity
        used_templates.append((chosen_template, named_entities, gender_of_entities))
        for ei, name in enumerate(named_entities):
            if name_boundary:
                xname = f"[{name}]"
            else:
                xname = name
            fact = fact.replace(f"ENT_{ei}_{gender_of_entities[ei]}", xname)
        story += fact + separator

    data_row["text_story"] = story
    data_row["used_templates"] = used_templates
    return data_row


def apply_templates(args, data_file, templates, split) -> List[Dict[str, Any]]:
    """

    data_file: consists of rows of json, with the following keys:
        - edges
        - query

    Apply the templator over the rows
    """
    new_rows = []
    log.info("Applying language layer ...")
    pb = tqdm(total=len(data_file))
    for row in data_file:
        try:
            new_row = copy.deepcopy(row)
            new_row = apply_template_on_edges(
                args,
                new_row,
                templates,
                name_boundary=args.use_name_boundary,
                split=split,
            )
            new_rows.append(new_row)
        except:
            pass
        pb.update(1)
    pb.close()
    if len(data_file) != len(new_rows):
        log.warn(
            f"Due to unavailability of some templates, number of rows reduced from {len(data_file)} to {len(new_rows)}."
        )
    log.info("Application complete!")
    return new_rows


def load_csv_templates(loc, ignore_incorrect=False) -> Dict[str, Any]:
    """
    Load csv templates and convert them to dict
    """
    print(f"Loading templates from {loc}...")
    df = pd.read_csv(loc)
    template_store = {}
    dropped = 0
    for i, row in df.iterrows():
        if ignore_incorrect:
            if not row["is_correct"]:
                dropped += 1
                continue
        if row["rel_comb"] not in template_store:
            template_store[row["rel_comb"]] = {}
        if row["gender_comb"] not in template_store[row["rel_comb"]]:
            template_store[row["rel_comb"]][row["gender_comb"]] = []
        if not row["ignore"]:
            template_store[row["rel_comb"]][row["gender_comb"]].append(row["template"])
    if dropped > 0:
        print(f"Dropped {dropped} templates because ignore_incorrect flag is set.")
    return template_store


def load_templates(args) -> Dict[str, Any]:
    """
    Load the correct template based on the type
    """
    templates = {"train": {}, "valid": {}, "test": {}}
    cur_folder = get_current_folder()
    synthetic_templates = json.load(
        open(cur_folder / args.template_folder / "synthetic" / "train.json")
    )
    template_dir = cur_folder / args.template_folder / args.template_type
    if args.template_type == "synthetic":
        templates["train"] = synthetic_templates
        templates["valid"] = synthetic_templates
        templates["test"] = synthetic_templates
    elif args.template_type == "amt":
        templates["train"] = load_csv_templates(
            template_dir / args.template_amt.train_file,
            ignore_incorrect=args.template_amt.ignore_incorrect,
        )
        templates["valid"] = load_csv_templates(
            template_dir / args.template_amt.valid_file,
            ignore_incorrect=args.template_amt.ignore_incorrect,
        )
        templates["test"] = load_csv_templates(
            template_dir / args.template_amt.test_file,
            ignore_incorrect=args.template_amt.ignore_incorrect,
        )
        templates["synthetic"] = synthetic_templates
    else:
        raise AssertionError(f"template_type : {args.template_type} not supported")
    return templates


def load_graphs(
    args,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Load graphs generated by GLC
    """
    loc = (
        Path(args.data_loc) / "rule_0"
    )  # rule_0 is the default location for Clutrr specific data
    train_file = loc / "train.jsonl"
    if not train_file.exists():
        raise AssertionError(f"train file not found in {loc}")
    val_file = loc / "valid.jsonl"
    if not val_file.exists():
        raise AssertionError(f"val file not found in {loc}")
    test_file = loc / "test.jsonl"
    if not test_file.exists():
        raise AssertionError(f"test file not found in {loc}")
    train_file = load_jsonl(train_file)
    val_file = load_jsonl(val_file)
    test_file = load_jsonl(test_file)
    return train_file, val_file, test_file


def validate_graphs(data_file):
    """GLC provides generic graphs, but certain relation combinations
    are not possible in CLUTRR, such as A->wife->B->husband->C or
        A->son->B->father->C (if A and C are in the same gender)
    Thus, prune the graphs where the resolution path consists of
        consecutive `SO,SO`, or `child,inv-child` or `inv-child,child`,
        or `grand-inv,grand`, or `inv-grand,grand`, `in-law,inv-in-law`, or
        `inv-in-law,in-law` or `un,inv-un` or `inv-un,un`
    """
    block_list = [
        "SO,SO",
        "child,inv-child",
        "inv-child,child",
        "grand-inv,grand",
        "inv-grand,grand",
        "in-law,inv-in-law",
        "inv-in-law,in-law",
        "un,inv-un",
        "inv-un,un",
    ]
    cleaned_rows = []
    for row in data_file:
        found = False
        for bl in block_list:
            if bl in row["descriptor"]:
                found = True
        if found:
            continue
        cleaned_rows.append(row)
    log.info(f"Cleaned rows from {len(data_file)} to {len(cleaned_rows)}")
    return cleaned_rows


def save_graphs(args, train_file, valid_file, test_file) -> None:
    """
    Overwrite the graphs in the same location
    """
    loc = (
        Path(args.data_loc) / "rule_0"
    )  # rule_0 is the default location for Clutrr specific data
    log.info(f"Saving {len(train_file)} train records.")
    dump_jsonl(train_file, loc / "train.jsonl")
    log.info(f"Saving {len(valid_file)} train records.")
    dump_jsonl(valid_file, loc / "valid.jsonl")
    log.info(f"Saving {len(test_file)} test records.")
    dump_jsonl(test_file, loc / "test.jsonl")


def subsample_graphs(
    args, train_file, valid_file, test_file
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    only subsample n rows as specified in config
    """
    if len(train_file) > args.num_train:
        train_file = random.sample(train_file, args.num_train)
    else:
        log.warn("Not enough valid files. Please generate more graphs using GLC.")
    if len(valid_file) > args.num_valid:
        valid_file = random.sample(valid_file, args.num_valid)
    else:
        log.warn("Not enough train files. Please generate more graphs using GLC.")
    if len(test_file) > args.num_test:
        test_file = random.sample(test_file, args.num_test)
    else:
        log.warn("Not enough test files. Please generate more graphs using GLC.")
    return train_file, valid_file, test_file


@hydra.main(config_name="config", version_base="1.1")
def main(args: DictConfig):
    set_seed(args.seed)
    console.rule("CLUTRR - Language Layer Applicator")
    console.print(args)
    # Load files
    train_file, valid_file, test_file = load_graphs(args)
    # validate graphs
    train_file = validate_graphs(train_file)
    valid_file = validate_graphs(valid_file)
    test_file = validate_graphs(test_file)
    ## Load templates
    templates = load_templates(args)
    ## Apply templates per file
    train_file = apply_templates(args, train_file, templates, "train")
    valid_file = apply_templates(args, valid_file, templates, "valid")
    test_file = apply_templates(args, test_file, templates, "test")
    # Subsample
    train_file, valid_file, test_file = subsample_graphs(
        args, train_file, valid_file, test_file
    )
    ## Save files
    log.info("Saving files ...")
    save_graphs(args, train_file, valid_file, test_file)
    log.info("Done.")


if __name__ == "__main__":
    main()
