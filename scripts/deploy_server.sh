#!/bin/bash
# script must be executed from root git directory

scripts/build_server.sh

# NB: 'preview should not be mandatory, I guess it's we use a pre-installed not up-to-date gcloud command line on travis, we should clean that
gcloud preview app deploy src/server/app.yaml --stop-previous-version --quiet

scripts/clean_server_build.sh