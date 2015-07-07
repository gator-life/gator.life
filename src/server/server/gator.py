import os
import webapp2
import jinja2

CGI_VARIABLE_SERVER_SOFTWARE = 'SERVER_SOFTWARE'

def is_dev_env_server():
    return os.environ.get(CGI_VARIABLE_SERVER_SOFTWARE, '').startswith('Dev')

DEBUG_MODE = is_dev_env_server()

class Link(object):
    def __init__(self, link, text):
        self.link = link
        self.text = text


class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')


        links = [
            Link(link='https://www.google.com', text='google.com'),
            Link(link='gator.life', text='gator.life')
        ]

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

# 'app' name is mandatory for webbapp
app = webapp2.WSGIApplication(ROUTING, debug=DEBUG_MODE) #pylint: disable=invalid-name



