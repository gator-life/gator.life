import sys
from time import sleep
import datetime
import logging
from vcr import use_cassette
from common.datehelper import utcnow
from topicmodeller.topicmodeller import TopicModeller
from server.dal import Dal
from server.environment import IS_TEST_ENV
from .userprofileupdater import update_profiles_in_database
from .updatemodel import ModelUpdater
from .scrap_and_learn import scrap_learn

LOGGER = logging.getLogger(__name__)


def update_model_profiles_userdocs():

    nb_args = len(sys.argv) - 1  # first argument is script name
    if nb_args < 1:
        print "command usage: python launch_backgroundupdate.py model_directory [vcr_cassette_file users_prefix nb_docs]"
        sys.exit(1)

    topic_model_directory = sys.argv[1]
    test_mode = nb_args == 4
    if test_mode and not IS_TEST_ENV:
        print "'TEST_ENV' environment variable should be set when 'test' arguments are specified"

    if test_mode:
        vcr_cassette_file = sys.argv[2]
        users_prefix = sys.argv[3]
        keep_user_func = lambda u: u.email.startswith(users_prefix)
        nb_docs_before_users_reload = int(sys.argv[4])
        start_cache_date = utcnow()
    else:
        vcr_cassette_file = None
        keep_user_func = lambda u: True
        nb_docs_before_users_reload = 100
        start_cache_date = utcnow() - datetime.timedelta(days=14)

    LOGGER.info(
        u'Start update_model_profiles_userdocs, '
        u'topic_model_directory[%s] '
        u'test_mode[%s] '
        u'vcr_cassette_file[%s] '
        u'nb_docs_before_users_reload[%s] '
        u'start_cache_date[%s]',
        topic_model_directory, test_mode, vcr_cassette_file, nb_docs_before_users_reload, start_cache_date)

    model_updater = ModelUpdater()
    topic_modeller = TopicModeller()
    topic_modeller.load(topic_model_directory)

    seen_url_hashes_set = set(Dal().doc.get_recent_doc_url_hashes(start_cache_date))

    with use_cassette(vcr_cassette_file, record_mode='none', ignore_localhost=True) if vcr_cassette_file else NoContext():
        while True:
            try:
                LOGGER.info("start new scrap_learn loop")
                dal = Dal()
                users = _get_users(dal, keep_user_func)
                model_updater.update_model_in_db(topic_modeller, users)
                update_profiles_in_database(users)
                scrap_learn(topic_modeller, users, nb_docs_before_users_reload, seen_url_hashes_set)
            except:  # pylint: disable=bare-except
                LOGGER.exception(u'Exception in update_model_profiles_userdocs main loop, restarting')
                sleep(30)
            if vcr_cassette_file:  # only one loop for run from a cassette
                return


class NoContext(object):

    def __init__(self):
        pass

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def _get_users(dal, keep_user_func):
    all_users = dal.user.get_all_users()
    users = [user for user in all_users if keep_user_func(user)]  # to filter in tests
    LOGGER.info("get_users: %s users found", len(users))
    return users
