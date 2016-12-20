#!/bin/bash

rm -rf global_env
rm -rf appengine_env
rm -rf lib
docker rmi -f  background_update
docker rmi -f  gator_deps

virtualenv global_env
source global_env/bin/activate
scripts/install_envs.sh
scripts/start_tests.sh

scripts/kill_gunicorn.sh
scripts/kill_gcloud.sh

scripts/run_pylint.sh