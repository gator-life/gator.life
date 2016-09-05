#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from server.handlers import handlers

# This variable is referenced by gunicorn in
#  - entrypoint section of app.yaml file,
#  - tools/start_server.sh
# if changed, gunicorn command must be updated accordingly.
APP = Flask(__name__, static_folder='server/static')
APP.register_blueprint(handlers)
APP.secret_key = 'maybe_we_should_generate_a_random_key'
