import logging
import google.cloud.logging  # pylint: disable=import-error
from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging  # pylint: disable=import-error
from common.environment import IS_DEV_ENV, IS_TEST_ENV


def init_gcloud_log(project_id, logger_name):
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if IS_DEV_ENV or IS_TEST_ENV:
        logging.basicConfig(filename=logger_name + u'.log', level=logging.DEBUG, format=log_format)
    else:
        # see: https://googlecloudplatform.github.io/google-cloud-python/latest/logging-usage.html#cloud-logging-handler
        # and https://github.com/GoogleCloudPlatform/getting-started-python/blob/master/6-pubsub/bookshelf/__init__.py#L40
        client = google.cloud.logging.Client(project_id)
        # NB: we should use AppEngineHandler for server at next google.cloud API update
        # https://googlecloudplatform.github.io/google-cloud-python/latest/logging-handlers-app-engine.html
        handler = CloudLoggingHandler(client, logger_name)
        handler.setFormatter(logging.Formatter(log_format))
        setup_logging(handler)
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger("readability.readability").setLevel(logging.WARNING)  # very verbose package


def shrink(string, max_length=500):
    origin_length = len(string)
    if origin_length <= max_length:
        return string
    kept_length = max_length / 2
    return string[:kept_length] + u'(...)' + string[-kept_length:]
