#!/bin/bash
# script must be executed from root git directory

# kill previous instance of flask server and free port if needed
pkill -f main.py
fuser -k 8080/tcp
# activate specific appengine virtual env to ensure that flask server
# only uses python libs available, that is the ones defined in requirements.txt
# next to server python module
source appengine_env/bin/activate
python src/server/server/main.py &
deactivate
tools/start_gcloud_and_exit.sh
# start Flask server and datastore in parallel, no need to wait for the first one
# because it's always faster to start that datastore