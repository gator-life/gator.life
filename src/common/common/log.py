import logging
import google.cloud.logging  # pylint: disable=import-error
from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging  # pylint: disable=import-error


def init_gcloud_log(project_id, logger_name, is_test_env):
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if not is_test_env:
        # see: https://googlecloudplatform.github.io/google-cloud-python/latest/logging-usage.html#cloud-logging-handler
        # and https://github.com/GoogleCloudPlatform/getting-started-python/blob/master/6-pubsub/bookshelf/__init__.py#L40
        client = google.cloud.logging.Client(project_id)
        # NB: we should use AppEngineHandler for server at next google.cloud API update
        # https://googlecloudplatform.github.io/google-cloud-python/latest/logging-handlers-app-engine.html
        handler = CloudLoggingHandler(client, logger_name)
        handler.setFormatter(logging.Formatter(log_format))
        setup_logging(handler)
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.basicConfig(filename=logger_name + u'.log', level=logging.DEBUG, format=log_format)
