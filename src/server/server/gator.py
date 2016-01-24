import os
import webapp2

import handlers # pylint: disable=relative-import
# problem (to solve) with app engine: server is not seen as a package by GAE
# so you can't do proper relative import (from . import dal)

CGI_VARIABLE_SERVER_SOFTWARE = 'SERVER_SOFTWARE'


def is_dev_env_server():
    return os.environ.get(CGI_VARIABLE_SERVER_SOFTWARE, '').startswith('Dev')

DEBUG_MODE = is_dev_env_server()

ROUTING = [
    ('/', handlers.LoginPageHandler),
    ('/home', handlers.HomePageHandler)
]

# 'app' name is the convention for webapp. It must match the suffix of the 'script' directive in app.yaml file
# cf. https://cloud.google.com/appengine/docs/python/config/appconfig
app = webapp2.WSGIApplication(ROUTING, debug=DEBUG_MODE)  # pylint: disable=invalid-name
