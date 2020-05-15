# Makefile for working with a Python module

##########################################################################
## REQUIREMENTS
#
# The following packages are required to run this makefile:
#   pytest 				For running tests
#   coverage 			For running test coverage
#   cloc 				For counting code
#   pylint 				For running linting on code
#   setuptools 			For creating distributions
#

##########################################################################
## VARIABLES

MODULE      = fooof
LINT_FILE   = _lint.txt

##########################################################################
## CODE COUNTING

# Run all counts
run_counts:
	@make count_size
	@make count_cloc
	@make count_cloc_tests

# Count the total number of lines in the module
count_size:
	@echo "\n\n CHECK MODULE SIZE:"
	@printf "\nNumber of lines of code & comments in the module: "
	@find ./$(MODULE) -name "*.py" -type f -exec grep . {} \; | wc -l

# Count code with CLOC, excluding test files
count_cloc:
	@printf "\n\n CLOC OUTPUT (EXCLUDING TESTS): \n"
	@cloc $(MODULE) --exclude-dir='tests'

# Count test code, with CLOC
count_cloc_tests:
	@printf "\n\n CLOC OUTPUT - TEST FILES: \n"
	@cloc $(MODULE)/tests --exclude-dir='test_files'

##########################################################################
## CODE TESTING

# Run all tests
run_tests:
	make coverage
	make doctests

# Run tests
tests:
	@pytest

# Run test coverage
coverage:
	@printf "\n\n RUN TESTS & TEST COVERAGE: \n"
	@coverage run --source $(MODULE) -m py.test
	@coverage report --omit="*/tests*"

# Run doctests
doctests:
	@printf "\n\n CHECK DOCTEST EXAMPLES: \n"
	@pytest --doctest-modules --ignore=$(MODULE)/tests $(MODULE)

##########################################################################
## CODE LINTING

# Run pylint and print summary
#   Note: --exit-zero is because for some reason pylint
#     throws an error otherwise. Unclear why.
run_lints:
	@printf "\n\n\n RUN PYLINT ACROSS MODULE: \n"
	@pylint $(MODULE) --ignore tests --exit-zero  > $(LINT_FILE)
	@tail -n4 $(LINT_FILE)

##########################################################################
## SUMMARY

# Run a summary of the module
summary:
	make run_counts
	make run_tests
	make run_lints

##########################################################################
## DISTRIBUTION

# Create a distribution build of the module
distribution:
	@python setup.py sdist bdist_wheel

# Clear out distribution files
clear_dist:
	@rm -rf build dist $(MODULE).egg-info
