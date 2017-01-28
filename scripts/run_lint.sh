#!/bin/bash
# script must be executed from root git directory
# run ESLInt and pylint, return 1 if at least one fails

# http://stackoverflow.com/questions/16080716/execute-multiple-commands-in-a-bash-script-sequentially-and-fail-if-at-least-one
EXIT_STATUS=0
# ESLint command is not in a dedicate script for local use because 'npm start' command already displays ESLint messages
src/client/node_modules/eslint/bin/eslint.js  src/client/src -c src/client/node_modules/react-scripts/.eslintrc || EXIT_STATUS=$?
python scripts/run_pylint.py src || EXIT_STATUS=$?
exit $EXIT_STATUS