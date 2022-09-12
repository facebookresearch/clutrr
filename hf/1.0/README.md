---
languages:
- en
licenses:
- unknown
multilinguality:
- monolingual
size_categories:
- 10K<n<100K
---

# Dataset Card for CLUTRR 

## Table of Contents

## Dataset Description
### Dataset Summary
**CLUTRR** (**C**ompositional **L**anguage **U**nderstanding and **T**ext-based **R**elational **R**easoning), a diagnostic benchmark suite, is first introduced in (https://arxiv.org/abs/1908.06177) to test the systematic generalization and inductive reasoning capabilities of NLU systems.  

The CLUTRR benchmark allows us to test a model’s ability for **systematic generalization** by testing on stories that contain unseen combinations of logical rules, and test for the various forms of **model robustness** by adding different kinds of superfluous noise facts to the stories.

### Dataset Task
CLUTRR contains a large set of semi-synthetic stories involving hypothetical families. The task is to infer the relationship between two family members, whose relationship is not explicitly mentioned in the given story.

Join the CLUTRR community in  https://www.cs.mcgill.ca/~ksinha4/clutrr/ 
## Dataset Structure
We show detailed information for all 14 configurations of the dataset.

### configurations:
**id**: a unique series of characters and numbers that identify each instance <br>
**story**: one semi-synthetic story involving hypothetical families<br>
**query**: the target query/relation which contains two names, where the goal is to classify the relation that holds between these two entities<br>
**target**: indicator for the correct relation for the query <br>
**target_text**: text for the correct relation for the query <br>
the indicator follows the rule as follows: <br> "aunt": 0, "son-in-law": 1, "grandfather": 2, "brother": 3,
    "sister": 4,
    "father": 5,
    "mother": 6,
    "grandmother": 7,
    "uncle": 8,
    "daughter-in-law": 9,
    "grandson": 10,
    "granddaughter": 11,
    "father-in-law": 12,
    "mother-in-law": 13,
    "nephew": 14,
    "son": 15,
    "daughter": 16,
    "niece": 17,
    "husband": 18,
    "wife": 19,
    "sister-in-law": 20  <br>
**clean\_story**: the story without noise factors<br>
**proof\_state**: the logical rule of the kinship generation <br>
**f\_comb**: the kinships of the query followed by the logical rule<br>
**task\_name**: the task of the sub-dataset in a form of "task_[num1].[num2]"<br> 
The first number [num1] indicates the status of noise facts added in the story: 1- no noise facts; 2- Irrelevant facts*; 3- Supporting facts*; 4- Disconnected facts*.<br>
The second number [num2] directly indicates the length of clauses for the task target.<br>
*for example:*<br>
*task_1.2 -- task requiring clauses of length 2 without adding noise facts*<br> 
*task_2.3 -- task requiring clauses of length 3 with Irrelevant noise facts added in the story*<br> 
**story\_edges**: all the edges in the kinship graph<br>
**edge\_types**: similar to the f\_comb, another form of the query's kinships followed by the logical rule <br>
**query\_edge**: the corresponding edge of the target query in the kinship graph<br>
**genders**: genders of names appeared in the story<br>
**task\_split**: train,test <br>

*Further explanation of Irrelevant facts, Supporting facts and Disconnected facts can be found in the 3.5 Robust Reasoning section in https://arxiv.org/abs/1908.06177

### Data Instances

An example of 'train'in Task 1.2 looks as follows.
```
{
  "id": b2b9752f-d7fa-46a9-83ae-d474184c35b6,
  "story": "[Lillian] and her daughter [April] went to visit [Lillian]'s mother [Ashley] last Sunday.",
  "query": ('April', 'Ashley'),
  "target": "grandmother",
  "clean_story": [Lillian] and her daughter [April] went to visit [Lillian]'s mother [Ashley] last Sunday.,
  "proof_state": [{('April', 'grandmother', 'Ashley'): [('April', 'mother', 'Lillian'), ('Lillian', 'mother', 'Ashley')]}],
  "f_comb": "mother-mother",
  "task_name": "task_1.2",
  "story_edges": [(0, 1), (1, 2)],
  "edge_types": ['mother', 'mother'],
  "query_edge": (0, 2),
  "genders": "April:female,Lillian:female,Ashley:female",
  "task_split": trian
}
```
### Data Splits

#### Data Split Name
(corresponding with the name used in the paper)

| task_split | split name in paper | train &validation task |test task |
| :---:   |  :---:  | :-: | :-: |
| gen_train23_test2to10 | data_089907f8 | 1.2, 1.3 | 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10 | 
| gen_train234_test2to10 | data_db9b8f04 | 1.2, 1.3, 1.4| 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10 |    
| rob_train_clean_23_test_all_23 | data_7c5b0e70 | 1.2,1.3 | 1.2, 1.3, 2.3, 3.3, 4.3 |   
| rob_train_sup_23_test_all_23 | data_06b8f2a1 | 2.2, 2.3 | 2.2, 2.3, 1.3, 3.3, 4.3 |  
| rob_train_irr_23_test_all_23 | data_523348e6 | 3.2, 3.3 | 3.2, 3.3, 1.3, 2.3, 4.3 |
| rob_train_disc_23_test_all_23 | data_d83ecc3e | 4.2, 4.3 | 4.2, 4.3, 1.3, 2.3, 3.3 |

#### Data Split Summary
Number of Instances in each split 

| task_split | train | validation | test |
| :-: |  :---: | :---: | :---: |
| gen_train23_test2to10   | 9074 | 2020 | 1146 |
| gen_train234_test2to10 | 12064 | 3019 | 1048 |
| rob_train_clean_23_test_all_23 | 8098 | 2026 | 447 |
| rob_train_disc_23_test_all_23 | 8080 | 2020 | 445 |
| rob_train_irr_23_test_all_23 | 8079 | 2020 | 444 |
| rob_train_sup_23_test_all_23 | 8123 | 2031 | 447 |


## Citation Information
```
@article{sinha2019clutrr,
  Author = {Koustuv Sinha and Shagun Sodhani and Jin Dong and Joelle Pineau and William L. Hamilton},
  Title = {CLUTRR: A Diagnostic Benchmark for Inductive Reasoning from Text},
  Year = {2019},
  journal = {Empirical Methods of Natural Language Processing (EMNLP)},
  arxiv = {1908.06177}
}
```