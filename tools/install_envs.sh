#!/bin/bash

# script must be executed from root git directory

mkdir lib

wget https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-119.0.0-linux-x86_64.tar.gz -nv
tar zxvf google-cloud-sdk-119.0.0-linux-x86_64.tar.gz -C lib
export PATH=$(pwd)/lib/google-cloud-sdk/bin:$PATH

pip install -r requirements.txt
pip install -r test_requirements.txt
# server unit tests are run in this "default" env so we need server requirements in it
pip install -r src/server/server/requirements.txt
pip install -e src/common -e src/scraper -e src/server -e src/topicmodeller -e src/learner -e src/orchestrator
python -m nltk.downloader stopwords punkt

#appengine_env env is used to run flask server in same context as on appengine
virtualenv appengine_env
appengine_env/bin/pip install -r src/server/server/requirements.txt
