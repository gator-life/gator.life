# [START imports]
import os

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]


# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())
# [END main_page]




app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
