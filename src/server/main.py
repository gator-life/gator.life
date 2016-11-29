#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from common.log import init_gcloud_log
from flask import Flask
from server.environment import IS_TEST_ENV, GCLOUD_PROJECT
from server.handlers import handlers

if not IS_TEST_ENV:
    import sys
    with open('local_deps.txt') as f:
        sys.path += f.readlines()

init_gcloud_log(GCLOUD_PROJECT, u'server', IS_TEST_ENV)
# This variable is referenced by gunicorn in
#  - entrypoint section of app.yaml file,
#  - tools/start_server.sh
# if changed, gunicorn command must be updated accordingly.
APP = Flask(__name__, static_folder='server/static')
APP.register_blueprint(handlers)
APP.secret_key = 'maybe_we_should_generate_a_random_key'


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.

    # to not risk to pollute database
    if not IS_TEST_ENV:
        raise Exception("TEST_ENV environment variable should be set for testing")
    if os.environ["DATASTORE_EMULATOR_HOST"] != "localhost:33001":
        raise Exception("DATASTORE_EMULATOR_HOST environment variable should be set to localhost:33001 for testing")

    APP.run(host='127.0.0.1', port=8080, debug=True)
