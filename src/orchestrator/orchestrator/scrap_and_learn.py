# -*- coding: utf-8 -*-

import logging
import datetime
import common.crypto as crypto
from common.technical import get_process_memory
from common.datehelper import utcnow
import learner.userdocmatch as userdocmatch
from scraper.scraper import Scraper
from server.frontendstructs import Document, UserDocument, FeatureVector
from server.dal import Dal
from server.environment import IS_TEST_ENV

LOGGER = logging.getLogger(__name__)


def scrap_learn(topic_model, users, nb_docs, seen_url_hashes_set):

    class NoActionSaver(object):

        def save(self, doc):
            pass

    scraper = Scraper(disconnected=IS_TEST_ENV)
    doc_saver = NoActionSaver()
    user_docs_max_size = 30
    docs_chunk_size = 1000

    _scrap_and_learn(scraper, doc_saver, topic_model, docs_chunk_size, user_docs_max_size, seen_url_hashes_set,
                     users, nb_docs)


def _scrap_and_learn(  # pylint: disable=too-many-arguments
        scraper, scraper_doc_saver, topic_modeller, docs_chunk_size, user_docs_max_size, seen_url_hashes_set,
        users, nb_docs):
    """
    internal scrap_learn so we can inject mocks
    """

    LOGGER.info(u'start scrap_learn, '
                u'docs_chunk_size[%s]'
                u'user_docs_max_size[%s]'
                u'seen_urls_hashes_set size[%s]'
                u'nb users[%s]'
                u'nb_docs[%s]'
                u'Memory(Mb)[%s]',
                docs_chunk_size, user_docs_max_size, len(seen_url_hashes_set), len(users), nb_docs,
                get_process_memory())

    doc_builder = DocBuilder(topic_modeller)
    scraper_filtered = ScraperFiltered(scraper, nb_docs, seen_url_hashes_set)
    doc_saver = UserDocSaverByChunk(docs_chunk_size, UserDocChunkSaver(), scraper_doc_saver)
    user_docs_accumulator = _build_user_docs_accumulator(users, user_docs_max_size)

    _execute_learn_loop(doc_builder, doc_saver, scraper_filtered, user_docs_accumulator, users)


def _execute_learn_loop(doc_builder, doc_saver, scraper_filtered, user_docs_accumulator, users):
    LOGGER.info(u'Start scrap_learn loop')
    for scraper_document, url_hash in scraper_filtered.scrap():

        (build_ok, doc) = doc_builder.build_doc(scraper_document, url_hash)
        if not build_ok:
            LOGGER.info(u'doc creation failed, url[%s]', scraper_document.url)
            continue
        LOGGER.debug(u'doc created, url[%s]', scraper_document.url)
        user_docs_accumulator.add_doc(doc, doc.feature_vector.vector)
        doc_saver.save_doc(doc, user_docs_accumulator, users)

    # exit function if scraper generator exited without error
    doc_saver.save_cached_docs(user_docs_accumulator, users)
    LOGGER.info(u'scraper exited, end scrap_learn loop')


class ScraperFiltered(object):

    def __init__(self, scraper, nb_docs, seen_url_hashes_set):
        self._scraper = scraper
        self._nb_docs = nb_docs
        self._url_hashes = seen_url_hashes_set
        self._current_doc_count = 0
        LOGGER.info(u'ScraperFiltered constructed with [%s] urls', len(self._url_hashes))

    def scrap(self):
        for doc in self._scraper.scrap():
            LOGGER.debug('scrapped doc[%s]', doc.url)
            if self._current_doc_count == self._nb_docs:
                LOGGER.info(u'nb_docs reached[%s], exit ScraperFiltered.Scrap', self._nb_docs)
                return
            self._current_doc_count += 1

            url_hash = crypto.hash_str(doc.url)
            if url_hash in self._url_hashes:
                LOGGER.info(u'duplicated url[%s]', doc.url)
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
        LOGGER.debug(u'save doc in UserDocSaverByChunk, url[%s]', doc.url)
        self._doc_immediate_saver.save(doc)
        self._doc_chunk.append(doc)
        if len(self._doc_chunk) == self._docs_chunk_size:
            LOGGER.info(u'Chunk size reached in UserDocSaverByChunk, save doc chunk, size[%s]', self._docs_chunk_size)
            self._save_and_clear(user_docs_accumulator, users)

    def save_cached_docs(self, user_docs_accumulator, users):
        self._save_and_clear(user_docs_accumulator, users)

    def _save_and_clear(self, user_docs_accumulator, users):
        self._user_doc_chunk_saver.save_user_docs_and_docs(self._doc_chunk, user_docs_accumulator, users)
        self._doc_chunk = []


class UserDocChunkSaver(object):

    def __init__(self):
        pass

    def save_user_docs_and_docs(self, doc_chunk, user_docs_accumulator, users):
        LOGGER.info(u'save doc chunk, size[%s]', len(doc_chunk))
        dal = Dal()
        dal.doc.save_documents(doc_chunk)
        user_to_user_docs = self._get_users_to_user_docs(users, user_docs_accumulator)
        dal.user_doc.save_users_docs(user_to_user_docs)

    @staticmethod
    def _get_users_to_user_docs(users, user_docs_accumulator):
        # udm: user doc matching
        udm_users_docs = user_docs_accumulator.build_user_docs()
        user_to_user_docs = (
            (user, [UserDocument(udm_user_doc.doc_id, udm_user_doc.grade)
                    for udm_user_doc in udm_user_docs])
            for user, udm_user_docs in zip(users, udm_users_docs)
        )
        return user_to_user_docs


class DocBuilder(object):

    def __init__(self, topic_modeller):
        self._topic_modeller = topic_modeller
        self._ref_feature_set_id = Dal().feature_set.get_ref_feature_set_id()

    def build_doc(self, scraper_document, url_hash):
        (classify_ok, topic_feature_vector) = self._topic_modeller.classify(scraper_document.content)
        if not classify_ok:
            return False, None
        doc = Document(
            scraper_document.url, url_hash, scraper_document.title, summary=scraper_document.content[:250],
            feature_vector=FeatureVector(topic_feature_vector, self._ref_feature_set_id))
        return True, doc


def _build_user_docs_accumulator(users, user_docs_max_size):

    def build_learner_user_data(user_feature_vector, user_docs):
        # Exclude old docs from user docs
        min_doc_date = utcnow() - datetime.timedelta(days=2)
        learner_user_docs = (userdocmatch.UserDoc(user_doc.document, user_doc.grade)
                             for user_doc in user_docs if user_doc.document.datetime > min_doc_date)
        return userdocmatch.UserData(user_feature_vector, learner_user_docs)

    dal = Dal()
    users_docs = dal.user_doc.get_users_docs(users)
    users_feature_vectors = dal.user_computed_profile.get_users_feature_vectors(users)
    user_data_list = (
        build_learner_user_data(feat_vec.vector, docs) for feat_vec, docs in zip(users_feature_vectors, users_docs)
    )
    user_docs_accumulator = userdocmatch.UserDocumentsAccumulator(user_data_list, user_docs_max_size)
    return user_docs_accumulator
