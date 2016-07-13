#!/bin/bash
# script must be executed from root git directory

# script used in pycharm because pycharm don't reuse the activated virtualenv (which is global_env for us)
# when running an external tool (here pylint)
source global_env/bin/activate
python tools/run_pylint.py src
