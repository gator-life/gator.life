#!/bin/bash

# script must be executed from root git directory

mkdir -p lib

rm -rf lib/google-cloud-sdk
wget https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-134.0.0-linux-x86_64.tar.gz -nv
tar zxf google-cloud-sdk-134.0.0-linux-x86_64.tar.gz -C lib
rm google-cloud-sdk-134.0.0-linux-x86_64.tar.gz

# install javascript / create-react-app dependencies
(cd src/client && npm install)

pip install -U pip # we need a recent version of pip so that pip install scipy/numpy works
pip install -r requirements.txt
pip install -r test_requirements.txt
# server unit tests are run in this "default" env so we need server requirements in it
pip install -r src/server/requirements.txt
pip install -e src/common -e src/scraper -e src/topicmodeller -e src/learner -e src/userdocmatch -e src/server -e src/orchestrator
python -m nltk.downloader stopwords punkt

#appengine_env env is used to run flask server in same context as on appengine
virtualenv appengine_env
appengine_env/bin/pip install -U pip
appengine_env/bin/pip install -r src/server/requirements.txt
python -m nltk.downloader -d src/server/nltk_data stopwords punkt
{ cat src/server/local_deps.txt; echo; } | while read line; do appengine_env/bin/pip install -e "src/$line"; done

git lfs pull
scripts/build_docker_gator_deps.sh