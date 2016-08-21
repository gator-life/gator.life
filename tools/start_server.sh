#!/bin/bash
# script must be executed from root git directory

. tools/set_env_vars.sh

# kill previous instance of flask server and free port if needed
# cf. http://stackoverflow.com/questions/3510673/find-and-kill-a-process-in-one-line-using-bash-and-regex 
kill $(ps aux | grep '[p]ython src/server/main.py' | awk '{print $2}')
fuser -k 8080/tcp
# use appengine virtual env to ensure that flask server only uses python libs available, that is the ones 
# defined in requirements.txt next to server python module.
appengine_env/bin/python  src/server/main.py &

tools/start_gcloud_and_exit.sh
# start Flask server and datastore in parallel, no need to wait for the first one
# because it's always faster to start that datastore