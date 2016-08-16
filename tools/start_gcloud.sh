#!/bin/bash

. tools/set_env_vars.sh

# kill previous instance of gcloud
tools/kill_gcloud.sh
lib/google-cloud-sdk/bin/gcloud --quiet beta emulators datastore start --project gator-01 --no-store-on-disk --host-port localhost:33001 --consistency=1.0