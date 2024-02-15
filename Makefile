# Makefile for working with a Python module

##########################################################################
## REQUIREMENTS
#
# This file requires certain dependencies for full functionality.
#
# The following Python packages are required:
#   pytest              For running tests
#   coverage            For running test coverage
#   pylint              For running linting on code
#   setuptools          For creating distributions
#   build               For creating distributions
#   twine               For checking and publishing distributions
#
# The following command line utilities are required:
#   cloc                For counting lines of code
#

##########################################################################
## VARIABLES

MODULE      = specparam
LINT_FILE   = _lint.txt

##########################################################################
## CODE COUNTING

# Run all counts
run-counts:
	@make count-size
	@make count-module
	@make count-tests

# Count the total number of lines in the module
count-size:
	@printf "\n\nCHECK MODULE SIZE:"
	@printf "\nNumber of lines of code & comments in the module: "
	@find ./$(MODULE) -name "*.py" -type f -exec grep . {} \; | wc -l

# Count module code with CLOC, excluding test files
count-module:
	@printf "\n\nCLOC OUTPUT - MODULE: \n"
	@cloc $(MODULE) --exclude-dir='tests'

# Count test code, with CLOC
count-tests:
	@printf "\n\nCLOC OUTPUT - TEST FILES: \n"
	@cloc $(MODULE)/tests --exclude-dir='test_files'

##########################################################################
## CODE TESTING

# Run all tests
run-tests:
	@make coverage
	@make doctests

# Run tests
tests:
	@printf "\n\nRUN TESTS: \n"
	@pytest

# Run test coverage
coverage:
	@printf "\n\nRUN TESTS: \n"
	@coverage run --source $(MODULE) -m pytest
	@printf "\n\nCHECK COVERAGE: \n"
	@coverage report --omit="*/tests*"

# Run doctests
doctests:
	@printf "\n\nCHECK DOCTEST EXAMPLES: \n"
	@pytest --doctest-modules --ignore=$(MODULE)/tests $(MODULE)

##########################################################################
## CODE LINTING

# Run pylint and print summary
#   Note: --exit-zero is because pylint throws an error when called
#     from a Makefile. Unclear why, but this avoids it stopping.
run-lints:
	@printf "\n\nRUN PYLINT ACROSS MODULE: \n"
	@pylint $(MODULE) --ignore tests --exit-zero  > $(LINT_FILE)
	@tail -n4 $(LINT_FILE)

##########################################################################
## SUMMARY

# Run a summary of the module
summary:
	@make run-counts
	@make run-tests
	@make run-lints

##########################################################################
## DISTRIBUTION

# Create a distribution build of the module
dist:
	@printf "\n\nCREATING DISTRIBUTION BUILD...\n"
	@python -m build
	@printf "\n\nDISTRIBUTION BUILD CREATED\n\n\n"

# Check a distribution build using twine
check-dist:
	@printf "\n\nCHECKING DISTRIBUTION BUILD:\n"
	@twine check dist/*
	@printf "\n"

# Clear out distribution files
clear-dist:
	@printf "\n\nCLEARING DISTRIBUTION FILES...\n"
	@rm -rf build dist $(MODULE).egg-info
	@printf "DISTRIBUTION FILES CLEARED\n\n\n"

# Show commands for publishing the distribution
#   Note: this doesn't run the commands (to avoid accidental publishing)
#   This also assumes that you are using twine + .pypirc
publish:
	@printf "\n\nTO PUBLISH THE DISTRIBUTION:\n\n"
	@printf "to testpypi: \n\ttwine upload --repository testpypi dist/*\n"
	@printf "to pypi: \n\ttwine upload --repository pypi dist/*\n\n"
