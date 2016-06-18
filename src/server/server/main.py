import os

from flask import Flask
from environment import IS_TEST_ENV  # pylint: disable=relative-import
from handlers import handlers  # pylint: disable=relative-import


APP = Flask(__name__)
APP.register_blueprint(handlers)
APP.secret_key = 'maybe_we_should_generate_a_random_key'

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.

    # to not risk to pollute database
    if not IS_TEST_ENV:
        raise Exception("IS_TEST_ENV environment variable should be set for testing")
    if os.environ["DATASTORE_HOST"] != "http://localhost:33001":
        raise Exception("DATASTORE_HOST environment variable should be set to http://localhost:33001 for testing")

    APP.run(host='127.0.0.1', port=8080, debug=True)
