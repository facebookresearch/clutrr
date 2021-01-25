# Test script for CLUTRR 2.0 generator with GLC

from clutrr.generator_glc import (
    set_seed,
    apply_gender,
    get_names,
    assign_names,
    apply_template_on_edges,
    apply_templates,
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
    args = Dict({"gender_map": "store/relations_store.yaml"})
    row = apply_gender(args, test_data[0])
    assert "descriptor_gender" in row
    assert type(row["descriptor_gender"]) == str
    assert len(row["descriptor_gender"].split(",")) == 4
    assert "gender_map" in row
    assert "target_gender" in row


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
            "gender_map": "store/relations_store.yaml",
            "num_names": 1000,
            "names_file": "names.csv",
            "names_url": names_url,
        }
    )
    row = assign_names(args, test_data[0])
    assert "name_map" in row
    assert len(row["name_map"]) == 5
    assert "named_edges" in row
    assert len(row["named_edges"]) == len(row["edges"])
