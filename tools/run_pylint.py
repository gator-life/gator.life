#!/usr/bin/env python

import os
import sys
import subprocess
import re

BASE_PATH = sys.argv[1]

FILE_NAME = re.compile(r'[-a-zA-Z0-9_/]*\.py')
CODE_RATING = re.compile('Your code has been rated at 10')

#NB: If you change it, you must also change it in .travis.yml
COMMAND = 'pylint src/server/server src/scraper/scraper src/common/common src/topicmodeller/classify.py src/topicmodeller/initialize_model.py src/topicmodeller/topicmodeller -f parseable'
TEST_COMMAND = 'pylint --rcfile=pylintrc_tests src/server/tests/*.py src/scraper/tests/*.py src/common/tests/*.py src/functests/*.py src/topicmodeller/tests/*.py -f parseable'


def run_pylint(command):
    os.chdir(BASE_PATH)
    print(command)
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
        return 1, output
    match = CODE_RATING.search(output)
    if not match:
        exitcode = 1
    else:
        exitcode = 0
    return exitcode, output


def add_file_paths(input):
    output = ''
    for line in input.split('\n'):
        if FILE_NAME.match(line):
            output += '%s/%s' % (BASE_PATH, line)
        else:
            output += line
        output += '\n'
    return output


def main():

    exitcode, output = run_pylint(COMMAND)
    output = add_file_paths(output)
    print output

    if exitcode != 0:
        print 'FAIL...Try, try again'
        sys.exit(1)

    exitcode_test, output_test = run_pylint(TEST_COMMAND)
    output_test = add_file_paths(output_test)
    print output_test

    if exitcode_test == 0:
        print 'You nailed it boy !'
        sys.exit(1)

    print 'Fail (just the tests)'
    sys.exit(1)



if __name__ == '__main__':
    main()

