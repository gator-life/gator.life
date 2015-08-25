import os
import webapp2
import jinja2
import dal  # pylint: disable=relative-import
# problem (to solve) with app engine: server is not seen as a package by GAE
# so you can't do proper relative import (from . import dal)

CGI_VARIABLE_SERVER_SOFTWARE = 'SERVER_SOFTWARE'

def is_dev_env_server():
    return os.environ.get(CGI_VARIABLE_SERVER_SOFTWARE, '').startswith('Dev')

DEBUG_MODE = is_dev_env_server()
NEW_USER_ID = "new_user_id"

class Link(object):
    def __init__(self, link, text):
        self.link = link
        self.text = text

class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        user_docs = dal.get_user_documents(NEW_USER_ID)
        links = [Link(link=user_doc.document.url, text=user_doc.document.title) for user_doc in user_docs]

        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_values = {
            'links': links
        }

        self.response.write(template.render(template_values))#pylint: disable=no-member
        # bug in pylint with jinja templates:
        # https://bitbucket.org/logilab/pylint/issue/490/jinja-templates-are-handled-as-str


ROUTING = [
    ('/', MainPageHandler),
]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

dal.init_user_dummy(NEW_USER_ID)

# 'app' name is the convention for webapp. It must match the suffix of the 'script' directive in app.yaml file
# cf. https://cloud.google.com/appengine/docs/python/config/appconfig
app = webapp2.WSGIApplication(ROUTING, debug=DEBUG_MODE) #pylint: disable=invalid-name






