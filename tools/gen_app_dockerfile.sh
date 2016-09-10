#!/bin/bash
# Script must be executed from root git directory

. tools/set_env_vars.sh

rm -f src/server/Dockerfile src/server/.dockerignore

# Generate Dockerfile and .dockerignore files
# echo "N" : Allow to respond "No" to the command asking if we want to update app.yaml to set runtime to custom.
echo "N" | lib/google-cloud-sdk/bin/gcloud beta app gen-config --config src/server/app.yaml --custom src/server

echo "ENV DATASTORE_HOST="$DATASTORE_HOST >> src/server/Dockerfile
echo "ENV TEST_ENV 'True'" >> src/server/Dockerfile
