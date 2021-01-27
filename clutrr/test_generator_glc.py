# Test script for CLUTRR 2.0 generator with GLC

import copy
from clutrr.generator_glc import (
    get_entity_gender_combination,
    load_templates,
    sample_combination,
    set_seed,
    apply_gender,
    get_names,
    assign_names,
    apply_template_on_edges,
    apply_templates,
    validate_graphs,
)

from addict import Dict

test_data = [
    {
        "edges": [
            [0, 1, "sibling"],
            [1, 2, "sibling"],
            [2, 3, "sibling"],
            [3, 4, "child"],
        ],
        "query": [0, 4, "un"],
        "target": "un",
        "descriptor": "sibling,sibling,sibling,child",
        "rules_used": ["sibling,child", "sibling,sibling", "sibling,sibling"],
        "rules_used_pos": [0, 0, 0],
        "resolution_path": [0, 1, 2, 3, 4],
    }
]

names_url = (
    "https://github.com/PhantomInsights/baby-names-analysis/raw/master/data/data.csv"
)


def test_apply_gender():
    set_seed(42)
    args = Dict({"gender_map": "clutrr/store/relations_store.yaml"})
    row = apply_gender(args, test_data[0])
    assert "descriptor_gender" in row
    assert type(row["descriptor_gender"]) == str
    assert len(row["descriptor_gender"].split(",")) == 4
    assert "gender_map" in row
    assert "target_gender" in row


def test_apply_gender_SO():
    # Hopefully we won't require this test once CLUTRR templates contain LGBTQ friendly templates
    set_seed(42)
    test_data = [
        {
            "edges": [
                [0, 1, "SO"],
                [1, 2, "child"],
                [2, 3, "child"],
                [3, 4, "sibling"],
            ],
            "query": [0, 4, "grand"],
            "target": "grand",
            "descriptor": "SO,child,child,sibling",
            "rules_used": ["SO,grand", "grand,sibling", "child,child"],
            "rules_used_pos": [0, 1, 1],
            "resolution_path": [0, 1, 2, 3, 4],
        }
    ]
    args = Dict({"gender_map": "clutrr/store/relations_store.yaml"})
    row = apply_gender(args, test_data[0])
    assert "gender_map" in row
    assert row["gender_map"][0] != row["gender_map"][1]


def test_get_names():
    args = Dict({"num_names": 1000, "names_file": "names.csv", "names_url": names_url})
    names = get_names(args)
    assert len(names) == 2000
    assert len(names[names.gender == "M"]) == 1000
    assert len(names[names.gender == "F"]) == 1000


def test_assign_names():
    set_seed(70)
    args = Dict(
        {
            "gender_map": "clutrr/store/relations_store.yaml",
            "num_names": 1000,
            "names_file": "clutrr/names.csv",
            "names_url": names_url,
        }
    )
    row = apply_gender(args, test_data[0])
    row = assign_names(args, row)
    assert "name_map" in row
    assert len(row["name_map"]) == 5
    assert "named_edges" in row
    assert len(row["named_edges"]) == len(row["edges"])


def test_get_entity_gender_combination():
    set_seed(42)
    args = Dict({"gender_map": "clutrr/store/relations_store.yaml"})
    row = apply_gender(args, test_data[0])
    entity, gender = get_entity_gender_combination(row, [1, 2])
    assert len(gender.split("-")) == 3
    assert entity == [1, 2, 3]
    entity, gender = get_entity_gender_combination(row, [2])
    assert len(gender.split("-")) == 2
    assert entity == [2, 3]


def test_sample_combination():
    set_seed(42)
    args = Dict(
        {
            "template_type": "amt",
            "gender_map": "clutrr/store/relations_store.yaml",
            "template_folder": "clutrr/templates",
            "num_names": 1000,
            "names_file": "clutrr/names.csv",
        }
    )
    row = apply_gender(args, test_data[0])
    row = assign_names(args, row)
    templates = load_templates(args)
    final_combination, edge_ids_group = sample_combination(
        args, row, templates["train"]
    )
    assert len(final_combination) == 2
    assert len(final_combination[1]) == 2
    assert final_combination[0] == 6
    assert len(edge_ids_group) == 2
    assert edge_ids_group[0] == [0, 1]
    assert edge_ids_group[1] == [2, 3]


def test_apply_template_on_edges():
    set_seed(42)
    args = Dict(
        {
            "template_type": "amt",
            "gender_map": "clutrr/store/relations_store.yaml",
            "template_folder": "clutrr/templates",
            "num_names": 1000,
            "names_file": "clutrr/names.csv",
        }
    )
    templates = load_templates(args)
    row = apply_template_on_edges(args, test_data[0], templates["train"])
    assert "text_story" in row
    assert "used_templates" in row
    # Recompute the story and test
    story = ""
    for chosen_template, named_entities, gender_of_entities in row["used_templates"]:
        fact = copy.deepcopy(chosen_template)
        for ei, name in enumerate(named_entities):
            fact = fact.replace(f"ENT_{ei}_{gender_of_entities[ei]}", name)
        story += fact + " "
    assert row["text_story"] == story


def test_validate_graphs():
    set_seed(42)
    test_data = [
        {
            "descriptor": "SO,child,child,sibling",
        },
        {
            "descriptor": "SO,SO,child,sibling",
        },
        {
            "descriptor": "SO,child,inv-child,sibling",
        },
        {
            "descriptor": "SO,child,inv-grand,grand",
        },
    ]
    cleaned_data = validate_graphs(test_data)
    assert len(cleaned_data) == 1
    assert cleaned_data[0]["descriptor"] == "SO,child,child,sibling"