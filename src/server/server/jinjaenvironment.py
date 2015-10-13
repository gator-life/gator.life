import os
import jinja2


_JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def render_template(html_file, attributes_dict):
    template = _JINJA_ENVIRONMENT.get_template(html_file)
    return template.render(attributes_dict)  # pylint: disable=no-member
    # bug in pylint with jinja templates:
    # https://bitbucket.org/logilab/pylint/issue/490/jinja-templates-are-handled-as-str
