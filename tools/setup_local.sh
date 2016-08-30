#!/bin/bash

rm -rf global_env
rm -rf appengine_env
rm -rf lib

virtualenv global_env
source global_env/bin/activate
tools/install_envs.sh
tools/start_tests.sh

tools/kill_flask_server.sh
tools/kill_gcloud.sh

tools/run_pylint.sh