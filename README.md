[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/x_k5a8eH)
# Project 5

**WARNING:** the type on the interface for `get_rule_dependency_graph` has changed from Project 4 to be `dict[int, list[int]]`. **You need to update the type from `dict[str, list[str]]` to `dict[int, list[int]]` after copying in the file from Project 4.**

Similar to Project 4, This project uses the `lexer` and `parser` functions from Project 1 and Project 2 to get an instance of a `DatalogProgram`. It also uses the `Interpreter.eval_schemes`, `Interpreter.eval_facts`, and `Interpreter.eval_queries` from Project 3.

Project 5 differs from Project 4 in that it must implement the `Interpreter.eval_eval_rules_optimized` function according to the algorithm specified in the project description on [learningsuite.byu.edu](http://learningsuite.byu.edu) in the _Content_ section under _Projects_ -> _Project 5_. This algorithm groups rules into strongly connected components (SCC), orders the components by dependency, and then evaluates the rules in each component to a fix-point. Here each component is considered separate from the other components meaning that there is a fix-point computed for each component and components are evaluated in the dependency order. This grouping and ordering minimizes the number of times each rule is evaluated.

You must track, and treat differently, _trivial_ SCCs. A trivial SCC is one that **only has a single rule and that rule does not depend on itself**. In other words, the rule does not have a self-loop in the dependency graph. If an SCC is trivial, then it only needs to be evaluated once! As such, the `Interpreter.eval_eval_rules_optimized` function should only yield one, and not two, evaluations for trivial SCCs. **All other non-trivial SCCs must iterate to a fix-point**.

You are expected to write tests for critical steps in the optimized algorithm. Specifically, you are expected to write tests for the dependency graph construction, finding the post-order rule ordering through a depth first search traversal, and computing SCCs. We recommend that the code for finding post-order numbers and computing SCCs be decoupled from the Datalog program and interpreter. Decoupling means that the code takes as input a dependency graph as specified by the `Interpreter.get_rule_dependency_graph` function. That graph has type `dict[int, list[int]]` where the key is the source rule and the list are the destination rules. An edge between rules is a dependency relation between the rules.

**Before proceeding further, please review the Project 5 project description, lecture slides, and all of the associated Jupyter notebooks. You can thank us later for the suggestion.**

## Developer Setup

Be sure to read the [WARNING](#warning) and [Copy Files](#copy-files) sections.

As in Project 3, the first step is to clone the repository created by GitHub Classroom when the assignment was accepted in a sensible directory. In the vscode terminal, `git clone <URL>` where `<URL>` is the one from GitHub Classroom after accepting the assignment. Or open a new vscode window, select _Clone Git Repository_, and paste the link they get when they hover over the "<> Code ▼" and copy the url

There is no need to install any vscode extensions. These should all still be present and active from the previous project. You do need to create the virtual environment, install the package, and install pre-commit. For a reminder to how that is done, see on [learningsuite.byu.edu](https://learningsuite.byu.edu) _Content_ &rarr; _Projects_ &rarr; _Projects Cheat Sheet_

  * Create a virtual environment: **be sure to create it in the `project-5` folder.** `python -m venv .venv`
  * Activate the virtual environment: `source .venv/bin/activate` or `.venv\Scripts\activate` for OSX and windows respectively.
  * Install the package in edit mode: `pip install --editable ".[dev]"`
  * Install pre-commit: `pre-commit install`

The above should result in a `project5` executable that is run from the command line in an integrated terminal. As before, be sure the integrated terminal is in the virtual environment.

### WARNING

  * Be sure that the `conda` environment is not active when setting up the project. It's active when there is a `(base)` annotation next to the terminal prompt. The `conda deactivate` command will exit that environment.
  * Be sure the Python version is at least 3.11 -- `python --version`.
  * Open the project folder in vscode when working on the project, and not a folder above it or below it, otherwise the paths for the pass-off tests will not work -- the common error is _"no project5 module found"_.
  * Be sure that vscode is using the virtual environment in the project folder: choose `Python Select Interpreter` from the command pallette and select the Python in the `.venv` folder -- its usually the first option if vscode opened that folder as the workspace.

## Files

  * `.devcontainer`: container definition for those using docker with vscode
  * `.github`: workflow definitions
  * `README.md`: overview and directions
  * `config_test.sh`: support for auto-grading -- **please do not edit**
  * `pyproject.toml`: package definition and project configuration -- **please do not edit**
  * `pytest.ini`: custom pytest marks for pass-off -- **please do not edit**
  * `src`: folder for the package source files
  * `tests`: folder for the package test files
  * `.gitignore`: files patterns that git should ignore

### Copy Files

Copy the below files from your solution to Project 3 into the `src/project5/` folder:

  * `datalogprogram.py`
  * `fsm.py`
  * `interpreter.py`
  * `lexer.py`
  * `parser.py`
  * `relation.py`
  * `./tests/test_relation.py`
  * `./tests/test_interpreter.py`

The `token.py` file is unchanged here and should not be copied over. Other test files from older projects can be copied as needed.

### Reminder

Please do not edit any of the following files or directories as they are related to _auto-grading_ and _pass-off_:

  * `config_test.sh`
  * `pytest.ini`
  * `./tests/test_passoff.py`
  * `./tests/resources/project5-passoff/*`

## Overview

The project is divided into the following modules each representing a key component of the project:

  * `src/project5/interpreter.py`: defines the `Interpreter` class with its interface.
  * `src/project5/project5.py`: defines the entry point for auto-grading and the command line entry point.
  * `src/project5/reporter.py`: defines functions for reporting the results of the interpreter.

Each of the above files are specified with Python _docstrings_ and they also have examples defined with python _doctests_. A _docstring_ is a way to document Python code so that the command `help(project5.relation)` in the Python interpreter outputs information about the module with it's functions and classes. For functions, the docstrings give documentation when the mouse hovers over the function in vscode.

### interpreter.py

The portion of the `Interpreter` class that needs to be implemented for Project 4 is `get_rule_dependency_graph` and `eval_rules_optimized`. The docstring describe what
each should do. There are no provided tests. **You are expected to write tests for the dependency graph and anything related to computing SCCS.**

**WARNING:** the type on the interface for `get_rule_dependency_graph` has changed from Project 4 to be `dict[int, list[int]]`. **You need to update the type from `dict[str, list[str]]` to `dict[int, list[int]]` after copying in the file from Project 4.**

### project5.py

The entry point for the auto-grader and the `project5` command. See the docstrings for details.

### reporter.py

A module for output matching in the pass-off tests. It takes the interface defined by `Interpreter` and converts the return types to strings that are used for the actual query reports that must output match for pass-off. _This module should work out of the box and not need to be touched_.

## Where to start

Here is the suggested order for Project 5:

1. Write a test for `get_rule_dependency_graph`
1. Implement `get_rule_dependency_graph`
1. Write a test for getting a reverse graph from a graph
1. Implement the reverse graph function
1. Write a test for computing the post-order sequence of nodes in a graph
1. Implement the function to compute the post-order-sequence of nodes in a graph
1. Write a test for computing SCCs for a graph
1. Implement the computing SCCs function -- the function must use the reverse and post-order functions
1. Write tests and implement `Interpreter.eval_rules_optimized`
1. Run the pass-off tests -- debug as needed.

## Pass-off and Submission

All the pass-off tests are in a single file: `tests/test-passoff.py`. Running individual tests is the same using either `pytest` directly or the testing pane in vscode (**recommended**).

The minimum standard for this project is **bucket 80**. That means that if all the tests pass in all buckets up to and including bucket 80, then the next project can be started safely.

The Project 5 submission follows that of the other projects:

  * Commit your solution on the master branch -- be sure to add any new files!
  * Push the commit to GitHub -- that should trigger the auto-grader
  * Goto [learningsuite.byu.edu](https://learningsuite.byu.edu) at _Assignments_ &rarr; _Projects_ &rarr; _Project 5_ to submit your GitHub ID and Project 5 URL for grading.
  * Goto the Project 5 URL, find the green checkmark or red x, and click it to confirm the auto-grader score matches the pass-off results from your system.

### Branches

Consider using a branch as you work on your submission so that you can `commit` your work from time to time. Once everything is working, and the auto-grader tests are passing, then you can `merge` your work into your master branch and push it to your GitHub repository. Ask your favorite search engine or LLM for help learning how to use Git feature branches.
