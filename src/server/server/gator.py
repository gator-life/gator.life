import os
import webapp2

import handlers  # pylint: disable=relative-import
# problem (to solve) with app engine: server is not seen as a package by GAE
# so you can't do proper relative import (from . import dal)

CGI_VARIABLE_SERVER_SOFTWARE = 'SERVER_SOFTWARE'


def is_dev_env_server():
    return os.environ.get(CGI_VARIABLE_SERVER_SOFTWARE, '').startswith('Dev')

DEBUG_MODE = is_dev_env_server()

ROUTING = [
    ('/login', handlers.LoginHandler),
    ('/register', handlers.RegisterHandler),
    ('/disconnect', handlers.DisconnectHandler),
    ('/link/(click_link|up_vote|down_vote)/(.*)', handlers.LinkHandler),
    ('/', handlers.HomeHandler),
]

CONFIGURATION = {}
CONFIGURATION['webapp2_extras.sessions'] = {
    'secret_key': 'maybe_we_should_generate_a_random_key',
}

# 'app' name is the convention for webapp. It must match the suffix of the 'script' directive in app.yaml file
# cf. https://cloud.google.com/appengine/docs/python/config/appconfig
app = webapp2.WSGIApplication(ROUTING, config=CONFIGURATION, debug=DEBUG_MODE)  # pylint: disable=invalid-name
