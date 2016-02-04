#!/usr/bin/env python

import os
import sys
import subprocess
import re

BASE_PATH = sys.argv[1]

FILE_NAME = re.compile(r'[-a-zA-Z0-9_/]*\.py$')
TEST_FOLDER_NAME = re.compile(r'tests')
CODE_RATING = re.compile('Your code has been rated at 10')

COMMAND = 'pylint -f parseable'
TEST_COMMAND = 'pylint --rcfile=pylintrc_tests -f parseable'


def files_list(base_folder, for_tests):
    result = []
    for root_folder, sub_folders, files in os.walk(base_folder):
        is_test_folder = TEST_FOLDER_NAME.search(root_folder) is not None
        if for_tests == is_test_folder:
            result += [os.path.join(root_folder, file) for file in files if FILE_NAME.match(file)]
    return ' '.join(result)


def run_pylint(command):
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
    exitcode, output = run_pylint(COMMAND + ' ' + files_list(BASE_PATH, for_tests=False))
    output = add_file_paths(output)
    print output

    if exitcode != 0:
        print 'FAIL...Try, try again'
        sys.exit(1)

    exitcode_test, output_test = run_pylint(TEST_COMMAND + ' ' + files_list(BASE_PATH, for_tests=True))
    output_test = add_file_paths(output_test)
    print output_test

    if exitcode_test == 0:
        print 'You nailed it boy !'
        sys.exit(0)

    print 'Fail (just the tests)'
    sys.exit(1)


if __name__ == '__main__':
    main()
