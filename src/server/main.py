#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from flask import Flask
from common.log import init_gcloud_log
from common.environment import IS_DEV_ENV, GCLOUD_PROJECT
from server.handlers import handlers
from server.reactapp import react
from server.api import api_blueprint

if not IS_DEV_ENV:
    import sys
    with open('local_deps.txt') as f:
        sys.path += f.readlines()

init_gcloud_log(GCLOUD_PROJECT, u'server')
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().info('start server logging')
# This variable is referenced by gunicorn in
#  - entrypoint section of app.yaml file,
#  - scripts/start_server.sh
# if changed, gunicorn command must be updated accordingly.
APP = Flask(__name__, static_folder='server/static')

APP.register_blueprint(handlers)
APP.register_blueprint(react)
APP.register_blueprint(api_blueprint)
APP.secret_key = 'maybe_we_should_generate_a_random_key'


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.

    # to not risk to pollute database
    if not IS_DEV_ENV:
        raise Exception("debug server only valid for development, DEV_ENV environment variable should be set")
    if os.environ["DATASTORE_EMULATOR_HOST"] != "localhost:33001":
        raise Exception("DATASTORE_EMULATOR_HOST environment variable should be set to localhost:33001 for testing")

    APP.run(host='127.0.0.1', port=8080, debug=True)
