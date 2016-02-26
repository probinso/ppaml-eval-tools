# PPAML eval tools

The PPAML client tools are a set of libraries and scripts that allow [PPAML](http://ppaml.galois.com/) TA2–4 teams to evaluate their own probabilistic programming systems in the same way that we will at Galois.

`peval` is the Program Evaluator tool used in evaluation and system use profiles of submitted Artifacts. Submited Artifacts are required to have two parts, an "engine" that designates the required general resources for an artifact to run, and a "solution" that performs some task using the resources in the engine.

### Installation

To install this program please use pip:
```
pip install --user .
```
If peval has installed already, you may need:
```
pip install --user --ignore-installed .
```

Note that there are not yet version related restrictions found in the required packages list.

### Teams
In order to keep track of who is providing artifacts, every team is assigned a number, as listed below:

| team.id | team.description |
| ------- |:----------------:|
| 1       |Integrator        |
| 3       |gamble            |
| 4       |BLOG              |
| 5       |{CH,D}imple       |
| 6       |Hakaru            |
| 7       |Venture           |
| 12      |Figaro            |

For now teams are static, and cannot be added by use of the peval tool.


### Challenge problems
Challenge problems also cannot be added through any `peval` command. They must be added in `db_init.sql`. The database can then be updated with `sqlite3 $PATH_TO_index.db < ./peval/db_init.sql`, which will rerun the initialization commands. Due to uniqueness constraints, this should be idempotent.


### Registering with `peval`
The command
```
$ peval register engine <team-id> <engine-directory>
```
registers the engine to a team, and prints out a unique identifying hash that we will call ENGHASH.

The command
```
$ peval register solution ENGHASH <problem-id> <solution-directory> \
                                  <config-path> [config-path ...]
```
will register the solution to it's engine, and designate what problem number is associated with the solution.


### Running with `peval`
The command
```
$ peval run <engine_hash> <solution_hash> <config_hash> <dataset_hash>
```
will do a single "run". Available run commands can be found by calling `driver-peval.py`, which will list combinations of available solutions, configs, and datasets. The run will have a unique run id.


### Evaluating with `peval`
The command
```
$ peval evaluate all
```
will evaluate all runs which have not already been (successfully, or unsuccessfully) evaluated.

The command
```
$ peval evaluate run <run_id>
```
will evaluate a single run. This can be used together with the `peval evaluate all` to evaluate a specific run.
