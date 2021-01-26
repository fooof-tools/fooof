# Contributing Guidelines

Thank you for your interest in contributing to `fooof`!

We welcome all contributions to the project that extend or improve code and/or documentation!

This page includes information for how to get involved and contribute to the project, and guidelines for how to do so.

This project adheres to a
[code of conduct](https://github.com/fooof-tools/fooof/blob/main/CODE_OF_CONDUCT.md)
that you are expected to uphold when participating in this project.

On this page, you can find information on:

* [Reporting a problem](#reporting-a-problem)
* [Getting involved in the project](#getting-involved)
* [Project scope](#project-scope)
* [Making a contribution](#making-a-contribution)
* [Project conventions](#project-conventions)

## Reporting a Problem

To report an issue with the code, please submit it to our [issue tracker](https://github.com/fooof-tools/fooof/issues).

In doing so, please try to include the following:

1. A short, top-level summary of the issue (usually 1-2 sentences)
2. A short, self-contained code snippet to reproduce the issue, ideally allowing a simple copy and paste to reproduce
   - Please do your best to reduce the code snippet to the minimum required
3. The actual outcome of the code snippet
4. The expected outcome of the code snippet

## Getting Involved

We welcome all kinds of contributions to the project, including suggested features and help with documentation, maintenance, and updates.

If you have a new idea you would like to suggest or contribute, please do the following:

1. Check if the idea is already being discussed on the
   [issues](https://github.com/fooof-tools/fooof/issues) or
   [development](https://github.com/fooof-tools/Development) page
2. Check that your idea is within the [project scope](#project-scope)
3. Open an [issue](https://github.com/fooof-tools/fooof/issues) describing
   what you would like to see added / changed, and why
4. Indicate in the issue if the idea is something you would be willing to help implement
   - if so, project maintainers can give feedback to help make a plan for the contribution
5. If you want to work on the contribution, follow the [contribution guidelines](#making-a-contribution) to do so

If you are interested in getting involved and helping with the project, a great place to start is to visit the
[issues](https://github.com/fooof-tools/fooof/issues) or
[development](https://github.com/fooof-tools/Development) page
and see if there is anything you would be interested in helping with. If so, join the conversation, and project developers can help get you started.

## Project Scope

All contributions must be within the scope of the module.

`fooof` is a module for parameterizing neural power spectra. This includes model fitting, management and analysis of resulting parameters, and utilities to visualize power spectra and model results. This module also includes functionality to simulate power spectra based on the model.

Procedures and utilities that do not deal with operating upon power spectra or on model outputs will most likely be considered out of scope. Notably, this model does not include doing spectral estimation or time-domain analysis. For approaches such as these, the [neurodsp](https://github.com/neurodsp-tools/neurodsp/) module may be a more appropriate target.

## Making a Contribution

If there is a feature you would like to add, or an issue you saw that you think you can help with, you are ready to make a submission to the project!

If you are working on a feature, please indicate so in the relevant issue, so that we can keep track of who is working on what.

Once you're ready to start working on your contribution, do the following:

1. [Fork this repository](https://help.github.com/articles/fork-a-repo/), which makes your own version of this project you can edit
2. [Make your changes](https://guides.github.com/activities/forking/#making-changes), updating or adding code to add the desired functionality
3. [Check the project conventions](#project-conventions), and make sure all new or updated code follows the guidelines
4. [Submit a pull request](https://help.github.com/articles/proposing-changes-to-a-project-with-pull-requests/), to start the process of merging the new code to the main branch

If it's your first time contributing to open source software, check out this free resource on [how to contribute to an open-source project on GitHub](https://app.egghead.io/courses/how-to-contribute-to-an-open-source-project-on-github).

## Project Conventions

All code contributed to the module should follow these conventions:

1. Code Requirements
    * All code should be written in Python, and run on the minimum required version that is noted in the README
    * New dependencies should be avoided if possible, especially if they are not in the Anaconda distribution
    * If any new dependencies are needed, they should be added to the `requirements.txt` file

2. Code Style
    * Code should generally follow [PEP8](https://www.python.org/dev/peps/pep-0008/) style guidelines
    * Max line length is 100 characters
    * Merge candidates will be checked using [pylint](https://www.pylint.org)

3. API & Naming Conventions
    * Try to keep the API consistent with existing code in terms of parameter names and ordering
    * Use standard casing, for example:
         * function names should be in snake_case (all lowercase with underscores)
         * class names should be in CamelCase (leading capitals with no separation)
    * If passing through arguments to an external function, the naming and ordering of parameters in this module should generally follow that of the external function

4. Code Documentation
    * All code should be documented, including in-code comments describing procedures, and detailed docstrings
    * Docstrings should follow the [numpy docs](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard) format
        * At minimum, there should be a sentence describing what the function does and a list of parameters and returns
        * Private functions should be indicated with a leading underscore, and should still include a docstring including at least a sentence describing what the function does
    * If possible, add an `Examples` section to the docstrings, that demonstrates a simple use case
        * If so, these examples should be executable, using [doctest](https://docs.python.org/3/library/doctest.html)
        * If examples cannot be run, use the SKIP directive

5. Code Tests
    * This project uses the [pytest](https://docs.pytest.org/en/latest/) testing tool for testing module code
    * All new code requires test code, written as unit tests that check each function and class in the module
    * Tests should be, at a minimum, 'smoke tests' that execute the code and check that it runs without raising an error
        * Where possible, accuracy checking is encouraged, though not strictly required
    * Merge candidates must pass all existing tests, and add new tests such as to not reduce test coverage
    * To run the tests locally, pytest needs to be installed (`pip install pytest`)
        * To run the tests on a local copy of the module, move into the folder and run `pytest .`

6. Documentation Website
    * This project uses a documentation website, created using [sphinx](https://www.sphinx-doc.org/)
    * Any new public functions or classes should be added to the `doc/api.rst` file, so they get included in the API list
    * Any new functionality should be added and described in the tutorials and/or examples
        * If a new approach is added, a new tutorial or example may be appropriate
    * To build and check the documentation locally:
        * Install the requirements for the docsite (`pip install -r requirements-doc.txt`)
        * Move to the `fooof/doc` directory (`cd doc`)
        * Run `make html` to create a local copy of the documentation website
        * The documentation can then be opened in a web browser by opening the file `fooof/doc/_build/html/index.html`

For more guidelines on how to write well formated and organized code, check out the [Python API Checklist](http://python.apichecklist.com).
