#!/bin/bash
# script must be executed from root git directory
pip install -r requirements.txt
pip install -r test_requirements.txt
# server unit tests are run in this "default" env so we need server requirements in it
pip install -r src/server/server/requirements.txt
pip install -e src/common -e src/scraper -e src/server -e src/topicmodeller -e src/learner -e src/orchestrator
python -m nltk.downloader stopwords punkt

#appengine_env env is used to run flask server in same context as on appengine
virtualenv appengine_env
source appengine_env/bin/activate
pip install -r src/server/server/requirements.txt
deactivate
