#!/bin/bash
# script must be executed from root git directory

. scripts/set_env_vars.sh

# kill previous instance of gunicorn server and free port if needed
scripts/kill_gunicorn.sh

# use appengine virtual env to ensure that flask app only uses python libs available, that is the ones
# defined in requirements.txt next to server python module.
# main:APP = a variable named APP (the web app) in main.py module.
appengine_env/bin/gunicorn -b 127.0.0.1:8080 main:APP --chdir src/server &

scripts/start_gcloud_and_exit.sh
# start gunicorn and datastore in parallel, no need to wait for the first one
# because it's always faster to start that datastore