# [START imports]
import os

import webapp2
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]


# [START main_page]
class MainPage(webapp2.RequestHandler):
    def get(self):

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())#pylint: disable=no-member
        # bug in pylint with jinja templates:
        # https://bitbucket.org/logilab/pylint/issue/490/jinja-templates-are-handled-as-str
# [END main_page]




APP = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
