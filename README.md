# CLUTRR

**C**ompositional **L**anguage **U**nderstanding with **T**ext-based **R**elational **R**easoniong

A benchmark dataset generator to test relational reasoning on text

Code for generating data for our paper ["CLUTRR: A Diagnostic Benchmark for Inductive Reasoning from Text"](https://arxiv.org/abs/1908.06177) at EMNLP 2019

- Blog: https://www.cs.mcgill.ca/~ksinha4/introducing-clutrr/
- Baselines: https://github.com/koustuvsinha/clutrr-baselines

### Dependencies

- [pandas](https://pypi.org/project/pandas/) - to store and retrieve in csv
- [tqdm](https://pypi.org/project/tqdm/) - for fancy progressbars
- [hydra](https://hydra.cc) - For config management

## Install

Ensure the GLC submodule is cloned:

`git submodule update --init --recursive`

Then, install the dependencies:

`pip install -r requirements.txt`

Finally, install the `clutrr` module.

`python setup.py develop`

**Note**: For the original full readme of v1.0, please switch to the main branch.

## Usage

To generate the graphs, change `DATA_LOC` path appropriately (full path), and run:

```
./generate.sh
```

The script first calls the [glc.py](glc/glc.py) script to compute the underlying graphs, and then calls the [clutrr/generator_glc.py](clutrr/generator_glc.py) to apply the language layer from our [AMT](clutrr/templates/amt/) or [synthetic](clutrr/templates/synthetic/) templates. The output is written in `jsonl` files in `$DATA_LOC/rule_0/{train/valid/test}.jsonl` defined in `generate.sh`. 

Each row of the output contains the following fields:

- `edges`: A list of triples (source node, sink node, relation) which consist of the story.
- `source`: The id of the source node.
- `sink`: The id of the sink node.
- `query`: A tuple of (`source`, `sink`)
- `target`: An un-gendered relation to predict (eg. _in-law_).
- `descriptor`: A combination of un-gendered relations which define the resolution path of the story.
- `rules_used`: List of the body of the rules used to construct the resolution path.
- `rules_used_pos`: The location in the resolution path where the rule was used. 
- `resolution_path`: The list of nodes starting from source to sink which constitute of the shortest path, and which can be resolved to get the target relation. 
- `noise_edges`: List of edges which are added to `edges` as noise.
- `descriptor_gender`: A string containing comma separated gendered relation of the descriptor.
- `target_gender`: The gendered relation to predict. (eg. _in-law_ can be either _father-in-law_ or _mother-in-law_)
- `gender_map`: Dictionary mapping the node id to their genders (male/female). 
- `name_map`: Dictionary mapping the node id to their names.
- `named_edges`: `edges` but with node ids replaced with names.
- `text_story`: The story generated after application of templates. Entities are highlighted in `[ ]`, which can be configured in settings.
- `used_templates`: List of exact templates used to generate the `text_story`. The list is a tuple of template, ordered entities corresponding to `ENT_x`, and ordered gender of the entities. 

## ChangeLog

### v1.3.0

- Fixes for incorrect AMT templates ([#15](https://github.com/facebookresearch/clutrr/issues/15)). Templates are now screened by a relation extraction model, and `is_correct` flag added to the data which indicates correct (`True`) and logically incorrect (`False`) templates.
- Added ability in the template loader to ignore incorrect templates: `template_amt.ignore_incorrect: True` in [config](clutrr/config.yaml).
- Added ability to load alternate template files by specifying in the config (`template_amt.{train/valid/test}_file` in [config](clutrr/config.yaml))
- Minor fixes to tests, added more requirements 

### v1.2.0

- Added support for noises (`supporting`, `disconnected` and `dangling`) from GLC
- Converted AMT templates to csv for better viewing / moderation. You can now skip a template by setting `ignore` field to `True`.
- Faster application of AMT templates to underlying graphs
- Added more documentation

### v1.1.0

- An example script is provided at `generate.sh`, which first calls the GLC module to generate graphs (which is added as a submodule), and then calls the `clutrr/generator_glc.py` script.
- We are now moving to use [Hydra](https://hydra.cc) for config management (#10). CLUTRR specific config is present at `config.yaml`. GLC specific config is present in `glc/graph_config.yaml`.
- We are deprecating the usage of `names` pip package in favour of the more comprehensive list https://github.com/PhantomInsights/baby-names-analysis.
- Tests are provided for most functions (use `pytest`).
- Output file fields will be documented in the next release.



## Tests

Install `pytest` (`pip install pytest`) and run the tests:

```sh
pytest clutrr
```

## Citation

If our work is useful for your research, consider citing it using the following bibtex:

```
@article{sinha2019clutrr,
  Author = {Koustuv Sinha and Shagun Sodhani and Jin Dong and Joelle Pineau and William L. Hamilton},
  Title = {CLUTRR: A Diagnostic Benchmark for Inductive Reasoning from Text},
  Year = {2019},
  journal = {Empirical Methods of Natural Language Processing (EMNLP)},
  arxiv = {1908.06177}
}
```

## Join the CLUTRR community

- Website: https://koustuvsinha.com/project/clutrr/

See the [CONTRIBUTING](CONTRIBUTING.md) file for how to help out.

## License

CLUTRR is CC-BY-NC 4.0 (Attr Non-Commercial Inter.) licensed, as found in the LICENSE file.
