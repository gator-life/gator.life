#!/bin/bash

# script must be executed from root git directory

mkdir -p lib

rm -rf lib/google-cloud-sdk
wget https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-122.0.0-linux-x86_64.tar.gz -nv
tar zxvf google-cloud-sdk-122.0.0-linux-x86_64.tar.gz -C lib
rm google-cloud-sdk-122.0.0-linux-x86_64.tar.gz

pip3 install -r requirements.txt
pip3 install -r test_requirements.txt
# server unit tests are run in this "default" env so we need server requirements in it
pip3 install -r src/server/requirements.txt
pip3 install -e src/common -e src/scraper -e src/server -e src/topicmodeller -e src/learner -e src/orchestrator
python3 -m nltk.downloader stopwords punkt

#appengine_env env is used to run flask server in same context as on appengine
python3 -m venv appengine_env
appengine_env/bin/pip install -r src/server/requirements.txt
