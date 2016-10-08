# -*- coding: utf-8 -*-

import logging
import sys
import datetime
from time import sleep
from common.datehelper import utcnow
import common.crypto as crypto
import learner.learner as lrn
from scraper.scraper import Scraper
from server.frontendstructs import Document, UserDocument, FeatureVector
from server.dal import Dal, REF_FEATURE_SET
from server.environment import IS_TEST_ENV
from topicmodeller.topicmodeller import TopicModeller


def scrap_and_learn():
    nb_args = len(sys.argv) - 1  # first argument is script name
    if nb_args < 1:
        print "command usage: python launch_scrap_and_learn.py model_directory [vcr_cassette_file users_prefix nb_docs]"
        sys.exit(1)

    topic_model_directory = sys.argv[1]
    test_mode = nb_args == 4
    if test_mode and not IS_TEST_ENV:
        print "'TEST_ENV' environment variable should be set when 'test' arguments are specified"

    class NoActionSaver(object):

        def save(self, doc):
            pass

    scraper = Scraper(disconnected=IS_TEST_ENV)
    doc_saver = NoActionSaver()
    user_docs_max_size = 30
    docs_chunk_size = 1000
    start_cache_date = utcnow() - datetime.timedelta(days=14)

    topic_modeller = TopicModeller.make_with_html_tokenizer()
    topic_modeller.load(topic_model_directory)

    if test_mode:
        vcr_cassette_file = sys.argv[2]
        users_prefix = sys.argv[3]
        nb_docs = int(sys.argv[4])
        start_cache_date = utcnow()
        keep_user_func = lambda u: u.email.startswith(users_prefix)
        import vcr
        with vcr.use_cassette(vcr_cassette_file, record_mode='none', ignore_localhost=True):
            _scrap_and_learn(scraper, doc_saver, topic_modeller, docs_chunk_size, user_docs_max_size, start_cache_date,
                             keep_user_func, nb_docs)
    else:
        _scrap_and_learn(
            scraper, doc_saver, topic_modeller, docs_chunk_size, user_docs_max_size, start_cache_date)

# NB: this function/module needs some refactoring (pylint)


def _scrap_and_learn(  # pylint: disable=too-many-arguments
        scraper, scraper_doc_saver, topic_modeller,
        docs_chunk_size, user_docs_max_size, seen_urls_cache_start_date,
        keep_user_func=lambda u: False, nb_docs=-1):
    # pylint: disable=too-many-locals
    dal = Dal()
    all_users = dal.get_all_users()
    users = [user for user in all_users if keep_user_func(user)]  # to filter in tests
    users_docs = dal.get_users_docs(users)
    users_feature_vectors = dal.get_users_feature_vectors(users)

    url_hashes = set(dal.get_recent_doc_url_hashes(seen_urls_cache_start_date))

    user_docs_accumulator = _build_user_docs_accumulator(users_docs, users_feature_vectors, user_docs_max_size)
    doc_chunk = [None] * docs_chunk_size
    index_in_docs_chunk = 0
    curr_nb_doc = 0
    # We need this high level loop to prevent crashes for whatever reason.
    #
    # For instance, exceptions are thrown by internal reddit generator, a generator cannot be continued after it raises an
    # exception, so we have to make another generator and restart The observed exception was due to a deficient connection.
    # We sleep to not flood logs (it won't come back immediately)
    while True:
        try:
            for scraper_document in scraper.scrap():
                if curr_nb_doc == nb_docs:
                    break
                curr_nb_doc += 1

                url_hash = crypto.hash_safe(scraper_document.link_element.url)
                if url_hash in url_hashes:
                    continue
                url_hashes.add(url_hash)

                (classify_ok, topic_feature_vector) = topic_modeller.classify(scraper_document.html_content)
                if not classify_ok:
                    continue

                doc = Document.make_from_scratch(
                    scraper_document.link_element.url, url_hash, scraper_document.link_element.origin_info.title,
                    summary=None, feature_vector=FeatureVector.make_from_scratch(topic_feature_vector, REF_FEATURE_SET))
                scraper_doc_saver.save(doc)
                doc_chunk[index_in_docs_chunk] = doc

                user_docs_accumulator.add_doc(doc, topic_feature_vector)

                index_in_docs_chunk += 1
                if index_in_docs_chunk == docs_chunk_size:
                    dal.save_documents(doc_chunk)
                    _save_users_docs_current_state(dal, users, user_docs_accumulator)
                    doc_chunk = [None] * docs_chunk_size
                    index_in_docs_chunk = 0

            # exit function if scraper generator exited without error
            dal.save_documents(doc_chunk[:index_in_docs_chunk])
            _save_users_docs_current_state(dal, users, user_docs_accumulator)
            return
        except Exception as exception:  # pylint: disable=broad-except
            logging.error("The orchestrator crashed! Starting it over ...")
            logging.exception(exception)
            sleep(30)


def _build_user_docs_accumulator(users_docs, users_feature_vectors, user_docs_max_size):
    def build_learner_user_data(user_feature_vector, user_docs):
        learner_user_docs = (lrn.UserDoc(user_doc.document, user_doc.grade) for user_doc in user_docs)
        return lrn.UserData(user_feature_vector, learner_user_docs)

    user_data_list = (
        build_learner_user_data(feat_vec.vector, docs) for feat_vec, docs in zip(users_feature_vectors, users_docs)
    )
    user_docs_accumulator = lrn.UserDocumentsAccumulator(user_data_list, user_docs_max_size)
    return user_docs_accumulator


def _save_users_docs_current_state(dal, users, user_docs_accumulator):
    lrn_users_docs = user_docs_accumulator.build_user_docs()
    user_to_user_docs = (
        (user, [UserDocument.make_from_scratch(lrn_user_doc.doc_id, lrn_user_doc.grade) for lrn_user_doc in lrn_user_docs])
        for user, lrn_user_docs in zip(users, lrn_users_docs)
    )
    dal.save_users_docs(user_to_user_docs)
