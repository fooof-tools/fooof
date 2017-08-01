#!/bin/sh

# Check how many lines there are in module - excludes blank lines
printf "\n\n\n\n CHECK MODULE SIZE:"
printf "\nNumber of lines of code & comments in ERP-SCANR: "
find ./fooof -name "*.py" -type f -exec grep . {} \; | wc -l

# Check number of files using cloc
printf "\n\n\n CLOC OUTPUT (EXCLUDING TESTS): \n"
cloc fooof --exclude-dir='tests'

#printf "\n\n\n CLOC OUTPUT - TEST FILES: \n"
#cloc fooof/tests --exclude-dir='data'

# Run Tests & Check Coverage
#printf "\n\n\n RUN TESTS & TEST COVERAGE: \n"
#coverage run --source fooof --omit="*/plts/*" -m py.test
#coverage report

# Find a way to get summary from pylint?
printf "\n\n\n RUN PYLINT ACROSS MODULE: \n"
pylint fooof -> _lint.txt
tail -n5 _lint.txt

# Print out some new lines
printf "\n\n\n"