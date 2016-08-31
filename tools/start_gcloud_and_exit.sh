#!/bin/bash
# script must be executed from root git directory

# start_gcoud.sh is blocking. This script wraps it to exit as soon
# as initialization is done (replace unreliable and slow wait call)
rm -f start_gcloud.log
touch start_gcloud.log
(tools/start_gcloud.sh 2>&1 | tee start_gcloud.log) &
{ tail -n +1 -f start_gcloud.log &} | sed -n '/Dev App Server is now running/q'
# inspired by the trick explained here:
# http://unix.stackexchange.com/questions/33018/have-bash-script-wait-for-status-message-before-continuing