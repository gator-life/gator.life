#!/bin/bash

HOME=/home/chronos/ /usr/share/google/dockercfg_update.sh
HOME=/home/chronos/ docker pull gcr.io/gator-01/background_update
docker run gcr.io/gator-01/background_update trained_topic_model
