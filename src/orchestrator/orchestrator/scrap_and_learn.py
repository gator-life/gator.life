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


def _scrap_and_learn(  # pylint: disable=too-many-arguments
        scraper, scraper_doc_saver, topic_modeller,
        docs_chunk_size, user_docs_max_size, seen_urls_cache_start_date,
        keep_user_func=lambda u: False, nb_docs=-1):

    dal = Dal()

    doc_builder = DocBuilder(topic_modeller)
    users = _get_users(dal, keep_user_func)
    scraper_filtered = ScraperFiltered(scraper, nb_docs, seen_urls_cache_start_date, dal)
    doc_saver = UserDocSaverByChunk(docs_chunk_size, UserDocChunkSaver(dal), scraper_doc_saver)
    user_docs_accumulator = _build_user_docs_accumulator(users, user_docs_max_size, dal)

    _execute_learn_loop(doc_builder, doc_saver, scraper_filtered, user_docs_accumulator, users)


def _execute_learn_loop(doc_builder, doc_saver, scraper_filtered, user_docs_accumulator, users):
    # We need this high level loop to prevent crashes for whatever reason.
    #
    # For instance, exceptions are thrown by internal reddit generator, a generator cannot be continued after it raises an
    # exception, so we have to make another generator and restart The observed exception was due to a deficient connection.
    # We sleep to not flood logs (it won't come back immediately)
    while True:
        try:
            for scraper_document, url_hash in scraper_filtered.scrap():

                (build_ok, doc) = doc_builder.build_doc(scraper_document, url_hash)
                if not build_ok:
                    continue

                user_docs_accumulator.add_doc(doc, doc.feature_vector.vector)
                doc_saver.save_doc(doc, user_docs_accumulator, users)

            # exit function if scraper generator exited without error
            doc_saver.save_cached_docs(user_docs_accumulator, users)
            return
        except Exception as exception:  # pylint: disable=broad-except
            logging.error("The orchestrator crashed! Starting it over ...")
            logging.exception(exception)
            sleep(30)


class ScraperFiltered(object):

    def __init__(self, scraper, nb_docs, seen_urls_cache_start_date, dal):
        self._scraper = scraper
        self._nb_docs = nb_docs
        self._url_hashes = set(dal.doc.get_recent_doc_url_hashes(seen_urls_cache_start_date))
        self._current_doc_count = 0

    def scrap(self):
        for doc in self._scraper.scrap():
            if self._current_doc_count == self._nb_docs:
                return
            self._current_doc_count += 1

            url_hash = crypto.hash_safe(doc.link_element.url)
            if url_hash in self._url_hashes:
                continue
            self._url_hashes.add(url_hash)
            yield doc, url_hash


class UserDocSaverByChunk(object):

    def __init__(self, docs_chunk_size, user_doc_chunk_saver, doc_immediate_saver):
        self._user_doc_chunk_saver = user_doc_chunk_saver
        self._doc_immediate_saver = doc_immediate_saver
        self._docs_chunk_size = docs_chunk_size
        self._doc_chunk = []

    def save_doc(self, doc, user_docs_accumulator, users):
        self._doc_immediate_saver.save(doc)
        self._doc_chunk.append(doc)
        if len(self._doc_chunk) == self._docs_chunk_size:
            self._save_and_clear(user_docs_accumulator, users)

    def save_cached_docs(self, user_docs_accumulator, users):
        self._save_and_clear(user_docs_accumulator, users)

    def _save_and_clear(self, user_docs_accumulator, users):
        self._user_doc_chunk_saver.save_user_docs_and_docs(self._doc_chunk, user_docs_accumulator, users)
        self._doc_chunk = []


def _get_users(dal, keep_user_func):
    all_users = dal.user.get_all_users()
    users = [user for user in all_users if keep_user_func(user)]  # to filter in tests
    return users


class UserDocChunkSaver(object):

    def __init__(self, dal):
        self._dal = dal

    def save_user_docs_and_docs(self, doc_chunk, user_docs_accumulator, users):
        self._dal.doc.save_documents(doc_chunk)
        self._save_users_docs_current_state(users, user_docs_accumulator)

    def _save_users_docs_current_state(self, users, user_docs_accumulator):
        lrn_users_docs = user_docs_accumulator.build_user_docs()
        user_to_user_docs = (
            (user, [UserDocument.make_from_scratch(lrn_user_doc.doc_id, lrn_user_doc.grade)
                    for lrn_user_doc in lrn_user_docs])
            for user, lrn_user_docs in zip(users, lrn_users_docs)
        )
        self._dal.user_doc.save_users_docs(user_to_user_docs)


class DocBuilder(object):

    def __init__(self, topic_modeller):
        self._topic_modeller = topic_modeller

    def build_doc(self, scraper_document, url_hash):
        (classify_ok, topic_feature_vector) = self._topic_modeller.classify(scraper_document.html_content)
        if not classify_ok:
            return False, None
        doc = Document.make_from_scratch(
            scraper_document.link_element.url, url_hash, scraper_document.link_element.origin_info.title,
            summary=None, feature_vector=FeatureVector.make_from_scratch(topic_feature_vector, REF_FEATURE_SET))
        return True, doc


def _build_user_docs_accumulator(users, user_docs_max_size, dal):
    def build_learner_user_data(user_feature_vector, user_docs):
        learner_user_docs = (lrn.UserDoc(user_doc.document, user_doc.grade) for user_doc in user_docs)
        return lrn.UserData(user_feature_vector, learner_user_docs)

    users_docs = dal.user_doc.get_users_docs(users)
    users_feature_vectors = dal.user_computed_profile.get_users_feature_vectors(users)
    user_data_list = (
        build_learner_user_data(feat_vec.vector, docs) for feat_vec, docs in zip(users_feature_vectors, users_docs)
    )
    user_docs_accumulator = lrn.UserDocumentsAccumulator(user_data_list, user_docs_max_size)
    return user_docs_accumulator
