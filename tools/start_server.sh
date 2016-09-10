#!/bin/bash
# script must be executed from root git directory

. tools/set_env_vars.sh

tools/start_gcloud_and_exit.sh

# kill running instance of the docker container if needed
tools/kill_docker_webapp.sh

tools/gen_app_dockerfile.sh

# Building and starting the app.
docker build -t "gator.life:dev-webapp" src/server
# -d option allow us to start the container in detached mode (detached from the console)
docker run -p 8080:8080 -d gator.life:dev-webapp

