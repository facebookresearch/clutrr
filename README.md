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

`pip install -r requirements.txt`

**Note**: Currently, CLUTRR is being updated to integrate [GLC](https://github.com/koustuvsinha/glc) in the develop branch (#9). This is a breaking change and hence it only supports clean graphs (devoid of noise) right now. In the following weeks this branch will be updated to replicate all of CLUTRR tasks. For the original full readme, please switch to the main branch.

## ChangeLog

### v1.1.0

- An example script is provided at `generate.sh`, which first calls the GLC module to generate graphs (which is added as a submodule), and then calls the `clutrr/generator_glc.py` script.
- We are now moving to use [Hydra](https://hydra.cc) for config management (#10). CLUTRR specific config is present at `config.yaml`. GLC specific config is present in `glc/graph_config.yaml`.
- We are deprecating the usage of `names` pip package in favour of the more comprehensive list https://github.com/PhantomInsights/baby-names-analysis.
- Tests are provided for most functions (use `pytest`).
- Output file fields will be documented in the next release.

## Usage

To generate the graphs, change `DATA_LOC` path appropriately (full path), and run:

```
./generate.sh
```

## Tests

Run the tests using `pytest`:

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

- Website: https://www.cs.mcgill.ca/~ksinha4/clutrr/

See the [CONTRIBUTING](CONTRIBUTING.md) file for how to help out.

## License

CLUTRR is CC-BY-NC 4.0 (Attr Non-Commercial Inter.) licensed, as found in the LICENSE file.
