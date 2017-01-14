# -*- coding: utf-8 -*-

import os

GCLOUD_PROJECT = 'gator-01'

# True if running unit and functional tests
IS_TEST_ENV = bool(os.environ.get('TEST_ENV', None))

# True if running test coverage analysis
IS_COVERAGE = bool(os.environ.get('COVERAGE', None))

# True in dev environment (IDE, debug, interactive test), False for ISO production / continuous integration
IS_DEV_ENV = bool(os.environ.get('DEV_ENV', None))
