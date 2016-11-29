#!/bin/bash
# script must be executed from root git directory
# copy local package dependencies to server folder
{ cat src/server/local_deps.txt; echo; } | while read line; do cp -R "src/$line/$line" src/server; done
# NB: 'preview should not be mandatory, I guess it's we use a pre-installed not up-to-date gcloud command line on travis, we should clean that
gcloud preview app deploy src/server/app.yaml --stop-previous-version --quiet

{ cat src/server/local_deps.txt; echo; } | while read line; do rm -r "src/server/$line"; done