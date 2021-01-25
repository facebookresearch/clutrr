#!/usr/bin/env python3
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
    print("Wrote {} records to {}".format(len(data), output_path))


def load_jsonl(input_path) -> list:
    """
    Read list of objects from a JSON lines file.
    """
    data = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line.rstrip("\n|\r")))
    print("Loaded {} records from {}".format(len(data), input_path))
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
    gd_map = yaml.load(open(args.gender_map), Loader=yaml.FullLoader)
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


def assign_names(args, data_row) -> Dict[int, str]:
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
    gd_map = yaml.load(open(args.gender_map), Loader=yaml.FullLoader)
    named_edges = []
    for edge in data_row["edges"]:
        er = [name_map[edge[0]], name_map[edge[1]]]
        gender_of_last = gender_map[edge[1]]
        er.append(gd_map[edge[2]][gender_of_last]["rel"])
        named_edges.append(er)
    data_row["named_edges"] = named_edges
    return data_row


def apply_template_on_edges(args, data_row, templates) -> Dict[str, Any]:
    """
    Apply templates on the edges
    :Return: modified data_row
    """
    data_row = apply_gender(args, data_row)
    data_row = assign_names(args, data_row)
    # TODO: select the entities to combine, and then apply template on top of it
    return data_row


def apply_templates(args, data_file, templates) -> List[Dict[str, Any]]:
    """

    data_file: consists of rows of json, with the following keys:
        - edges
        - query

    Apply the templator over the rows
    """
    pass


def load_templates(args) -> Dict[str, Any]:
    """
    Load the correct template based on the type
    """
    templates = {"train": {}, "valid": {}, "test": {}}
    cur_folder = Path(hydra.utils.get_original_cwd())
    if args.template_type == "synthetic":
        tp = json.load(open(cur_folder / args.template_folder / "train.json"))
        templates["train"] = tp
        templates["valid"] = tp
        templates["test"] = tp
    elif args.template_type == "amt":
        templates["train"] = json.load(
            open(cur_folder / args.template_folder / "train.json")
        )
        templates["valid"] = json.load(
            open(cur_folder / args.template_folder / "valid.json")
        )
        templates["test"] = json.load(
            open(cur_folder / args.template_folder / "test.json")
        )
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


@hydra.main(config_name="config")
def main(args: DictConfig):
    set_seed(args.seed)
    # Load files
    train_file, valid_file, test_file = load_graphs(args)
    ## Load templates
    templates = load_templates(args)
    ## Apply templates per file
    train_file = apply_templates(args, train_file, templates["train"])
    valid_file = apply_templates(args, valid_file, templates["valid"])
    test_file = apply_templates(args, test_file, templates["test"])
    ## Save files
    ##
    print("Done")


if __name__ == "__main__":
    main()
