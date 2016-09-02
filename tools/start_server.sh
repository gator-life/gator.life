#!/bin/bash
# script must be executed from root git directory

. tools/set_env_vars.sh

# kill previous instance of flask server and free port if needed
tools/kill_flask_server.sh
# use appengine virtual env to ensure that flask server only uses python libs available, that is the ones 
# defined in requirements.txt next to server python module.
#appengine_env/bin/python  src/server/main.py &
cd src/server
../../appengine_env/bin/gunicorn -b :8080 main:APP &
cd ../..

tools/start_gcloud_and_exit.sh
# start Flask server and datastore in parallel, no need to wait for the first one
# because it's always faster to start that datastore