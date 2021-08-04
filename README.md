# CLUTRR

**C**ompositional **L**anguage **U**nderstanding with **T**ext-based **R**elational **R**easoniong

A benchmark dataset generator to test relational reasoning on text

Code for generating data for our paper ["CLUTRR: A Diagnostic Benchmark for Inductive Reasoning from Text"](https://arxiv.org/abs/1908.06177) at EMNLP 2019

* Blog: https://www.cs.mcgill.ca/~ksinha4/introducing-clutrr/
* Baselines: https://github.com/koustuvsinha/clutrr-baselines

### Dependencies

- [pandas](https://pypi.org/project/pandas/) - to store and retrieve in csv
- [names](https://pypi.org/project/names/) - to generate fancy names
- [tqdm](https://pypi.org/project/tqdm/) - for fancy progressbars

## Install

`python setup.py develop`

## Tasks

CLUTRR is highly modular and thus can be used for various probing tasks. Here we document the various types of tasks
available and the corresponding config arguments to generate them. To
run a task, refer the following table and run:

`python main.py --train_task <> --test_tasks <> <args>`

Where, `train_task` is in the form of `<task_id>.<relation_length>`, and `test_tasks` is a comma separated list of the same form. For eg:

`python main.py --train_tasks 1.3 --test_tasks 1.3,1.4`

You can provide general arguments as well, which are defined in the next section.

| Task | Description                              |
|------|------------------------------------------|
|   1  | Basic family relations, free of noise   |
|   2  | Family relations with supporting facts  |
|   3  | Family relations with irrelevant facts  |
|   4  | Family relations with disconnected facts |
|   5  | Family relations with all facts (2-4)  |
|   6  | Family relations - Memory task: retrieve the relations already defined in the text 
|   7  | Family relations - Mix of Memory and Reasoning - 1 & 6 |   


Generated data is stored in `data/` folder.
i
## Generalizability

Each task mentioned above can be used for different length _k_ of the relations.
For example, Task 1 can have a train set of k=3 and test set of k=4,5,6, etc. See the
above section in how to provide such arguments quickly.


## AMT Paraphrasing

We collect paraphrases for relations k=1,2 and 3 from Amazon Mechanical Turk using [ParlAI](https://github.com/facebookresearch/parlai)
MTurk interface. The collected paraphrases can be re-used as _templates_ to generate
arbitrary large dataset in the above configurations. We will release the templates shortly here.

To use the templates, pass `--use_mturk_template` flag and location of the template using 
`--template_file` argument. The flag `--template_length` is optional and it governs
the maximum length k to use to replace the sentences. The script auto-downloads our collected and cleaned
template files from the server using `setup()` method in main.py.

## Transductive and Inductive Setting

CLUTRR provides both transductive and inductive setting for relational reasoning. In the transductive setting, the relation patterns encountered in the training set is the same as in the test set. While this setup is not interesting, it can be used to perform basic sanity checks of the model. In the inductive setting, the relation patterns are split 80-20 in training and testing. Furthermore, with the ability to split AMT placeholders, CLUTRR provides 4 scenarios to play with using the correct flags:

| Setup | Flags | Description |
| --- | ------ | ----- |
| (1) | (default)                  | same pattern in train & test, same AMT placeholder = EASY as data leak |
| (2) | `--template_split`           | same pattern in train & test, different AMT placeholder = Transductive, medium difficulty |
| (3) | `--holdout`                  | different pattern in train & test, same AMT placeholder = Inductive, but still could be easy for language models to exploit on the syntax |
| (4) | `--template_split --holdout` | different pattern in train & test, different AMT placeholder = Inductive, and hardest setup |

Thanks to [@NicolasAG](https://github.com/NicolasAG) for adding this information in the README.

## Rules

We create an ideal simple kinship world, which is derived from a set of _clauses_ or rules.
The rules are defined in [rules_store.yaml](clutrr/store/rules_store.yaml) file.

## Usage

To generate the simple setup on task 1, first cd into `clutrr/clutrr` folder, and run:

```
python main.py --train_tasks 1.2 --test_tasks 1.2 --train_rows 500 --test_rows 10 --equal --holdout --use_mturk_template --data_name "Robust Reasoning - clean - AMT" --unique_test_pattern
```

Pre-generated datasets used in our paper [can be found here](https://drive.google.com/file/d/1SEq_e1IVCDDzsBIBhoUQ5pOVH5kxRoZF/view).

#### CLI Usage

```
usage: main.py [-h] [--max_levels MAX_LEVELS] [--min_child MIN_CHILD]
               [--max_child MAX_CHILD] [--p_marry P_MARRY] [--boundary]
               [--output OUTPUT] [--rules_store RULES_STORE]
               [--relations_store RELATIONS_STORE]
               [--attribute_store ATTRIBUTE_STORE] [--train_tasks TRAIN_TASKS]
               [--test_tasks TEST_TASKS] [--train_rows TRAIN_ROWS]
               [--test_rows TEST_ROWS] [--memory MEMORY]
               [--data_type DATA_TYPE] [--question QUESTION] [-v]
               [-t TEST_SPLIT] [--equal] [--analyze] [--mturk] [--holdout]
               [--data_name DATA_NAME] [--use_mturk_template]
               [--template_length TEMPLATE_LENGTH]
               [--template_file TEMPLATE_FILE] [--template_split]
               [--combination_length COMBINATION_LENGTH]
               [--output_dir OUTPUT_DIR] [--store_full_puzzles]
               [--unique_test_pattern]

optional arguments:
  -h, --help            show this help message and exit
  --max_levels MAX_LEVELS
                        max number of levels
  --min_child MIN_CHILD
                        max number of children per node
  --max_child MAX_CHILD
                        max number of children per node
  --p_marry P_MARRY     Probability of marriage among nodes
  --boundary            Boundary in entities
  --output OUTPUT       Prefix of the output file
  --rules_store RULES_STORE
                        Rules store
  --relations_store RELATIONS_STORE
                        Relations store
  --attribute_store ATTRIBUTE_STORE
                        Attributes store
  --train_tasks TRAIN_TASKS
                        Define which task to create dataset for, including the
                        relationship length, comma separated
  --test_tasks TEST_TASKS
                        Define which tasks including the relation lengths to
                        test for, comma separaated
  --train_rows TRAIN_ROWS
                        number of train rows
  --test_rows TEST_ROWS
                        number of test rows
  --memory MEMORY       Percentage of tasks which are just memory retrieval
  --data_type DATA_TYPE
                        train/test
  --question QUESTION   Question type. 0 -> relational, 1 -> yes/no
  -v, --verbose         print the paths
  -t TEST_SPLIT, --test_split TEST_SPLIT
                        Testing split
  --equal               Make sure each pattern is equal. Warning: Time
                        complexity of generation increases if this flag is
                        set.
  --analyze             Analyze generated files
  --mturk               prepare data for mturk
  --holdout             if true, then hold out unique patterns in the test set
  --data_name DATA_NAME
                        Dataset name
  --use_mturk_template  use the templating data for mturk
  --template_length TEMPLATE_LENGTH
                        Max Length of the template to substitute
  --template_file TEMPLATE_FILE
                        location of placeholders
  --template_split      Split on template level
  --combination_length COMBINATION_LENGTH
                        number of relations to combine together
  --output_dir OUTPUT_DIR
                        output_dir
  --store_full_puzzles  store the full puzzle data in puzzles.pkl file.
                        Warning: may take considerable amount of disk space!
  --unique_test_pattern
                        If true, have unique patterns generated in the first
                        gen, and then choose from it.
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

## Papers using CLUTRR

- Nicolas Gontier, Koustuv Sinha, Siva Reddy, Chris Pal, _Measuring Systematic Generalization in Neural Proof Generation with Transformers_ (NeurIPS 2020) [Paper](https://arxiv.org/abs/2009.14786) [Code & Data](https://github.com/NicolasAG/SGinPG)
- Pasquale Minervini, Sebastian Riedel, Pontus Stenetorp, Edward Grefenstette, Tim Rocktäschel, _Learning Reasoning Strategies in End-to-End Differentiable Proving_ (ICML 2020) [Paper](https://arxiv.org/abs/2007.06477) [Code & Data](https://github.com/uclnlp/ctp)

## Join the CLUTRR community

* Website: https://www.cs.mcgill.ca/~ksinha4/clutrr/
* Using CLUTRR in your paper? Feel free to [send me an email](mailto:koustuv.sinha@mail.mcgill.ca) to include your paper in our README!

See the [CONTRIBUTING](CONTRIBUTING.md) file for how to help out.

## License
CLUTRR is CC-BY-NC 4.0 (Attr Non-Commercial Inter.) licensed, as found in the LICENSE file.

