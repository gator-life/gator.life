#!/bin/bash
# script must be executed from root git directory
# 1) Build docker image
scripts/build_docker_gator_deps.sh
scripts/build_docker_background_update.sh
# 2) Tag it to be compliant with gcr (google container repository) repo naming
# https://cloud.google.com/container-registry/docs/pushing
docker tag background_update gcr.io/gator-01/background_update
# 3) Push docker image to gcr
gcloud --quiet docker -- push gcr.io/gator-01/background_update

# 4) update startup script of the VM instance, this script:
# 4.1) dockercfg_update.sh so VM has access to gcr
# 4.2) pull the docker image
# 4.3) run the container
# the two commands cannot be executed as root by default (readonly folders)
# the workaround (prefix HOME=/home/chronos/) is given in SO link below 
# https://cloud.google.com/container-optimized-os/docs/how-to/run-container-instance#accessing_private_google_container_registry
# https://cloud.google.com/compute/docs/startupscript
# https://stackoverflow.com/questions/38520729/docker-login-with-root-user-on-container-vm-image
gcloud compute instances add-metadata background-update --metadata-from-file startup-script=scripts/background_update_startup.sh --quiet

# 5) restart the VM instance to force reloading updated docker image
# https://cloud.google.com/compute/docs/instances/restarting-an-instance
gcloud compute instances reset background-update --quiet