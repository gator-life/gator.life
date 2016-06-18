#!/bin/bash
# script must be executed from root git directory
source global_env/bin/activate
python tools/run_pylint.py src
