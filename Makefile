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
#
# The following command line utilities are required:
#   cloc                For counting lines of code
#

##########################################################################
## VARIABLES

MODULE      = fooof
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
	@coverage run --source $(MODULE) -m py.test
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
	@python setup.py sdist bdist_wheel
	@printf "\n\nDISTRIBUTION BUILD CREATED\n\n\n"

# Clear out distribution files
clear-dist:
	@printf "\n\nCLEARING DISTRIBUTION FILES...\n"
	@rm -rf build dist $(MODULE).egg-info
	@printf "DISTRIBUTION FILES CLEARED\n\n\n"
