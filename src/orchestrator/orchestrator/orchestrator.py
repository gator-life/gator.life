#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import datetime
import logging
from time import sleep
import jsonpickle

import learner.learner as lrn
from scraper.scraper import Scraper
from server.frontendstructs import Document, UserDocument
import server.dal as dal
from topicmodeller.topicmodeller import TopicModeller


def _setup_env():
    # set unicode and pretty-print
    jsonpickle.set_encoder_options('simplejson', indent=4, ensure_ascii=False)


class DocSaver(object):
    def __init__(self, folder):
        self.folder = folder

    def save(self, document):
        json = jsonpickle.encode(document)
        filename = self.folder + '/' + str(datetime.datetime.utcnow()) + '.json'
        with codecs.open(filename=filename, mode='w', encoding='utf-8') as file_desc:
            file_desc.write(json)


def orchestrate(scraper_output_folder, tm_data_folder):
    _setup_env()
    user_docs_max_size = 30
    docs_chunk_size = 1000

    topic_modeller = TopicModeller.make()
    topic_modeller.load(tm_data_folder)
    scraper = Scraper()

    _orchestrate(scraper, DocSaver(scraper_output_folder), topic_modeller, docs_chunk_size, user_docs_max_size)


def _orchestrate(scraper, scraper_doc_saver, topic_modeller, docs_chunk_size, user_docs_max_size):
    users = dal.get_all_users()
    users_docs = dal.get_users_docs(users)
    users_feature_vectors = dal.get_users_feature_vectors(users)
    user_docs_accumulator = _build_user_docs_accumulator(users_docs, users_feature_vectors, user_docs_max_size)
    doc_chunk = [None] * docs_chunk_size
    index_in_docs_chunk = 0
    # We need this high level loop to prevent crashes for whatever reason.
    #
    # For instance, exceptions are thrown by internal reddit generator, a generator cannot be continued after it raises an
    # exception, so we have to make another generator and restart The observed exception was due to a deficient connection.
    # We sleep to not flood logs (it won't come back immediately)
    while True:
        try:
            for scraper_document in scraper.scrap():
                doc = Document.make_from_scratch(
                    scraper_document.link_element.url, scraper_document.link_element.origin_info.title, summary=None)
                scraper_doc_saver.save(doc)
                doc_chunk[index_in_docs_chunk] = doc
                topic_feature_vector = topic_modeller.classify(scraper_document.html_content)
                user_docs_accumulator.add_doc(doc, topic_feature_vector)

                index_in_docs_chunk += 1
                if index_in_docs_chunk == docs_chunk_size:
                    dal.save_documents(doc_chunk)
                    _save_users_docs_current_state(users, user_docs_accumulator)
                    doc_chunk = [None] * docs_chunk_size
                    index_in_docs_chunk = 0

            # exit function if scraper generator exited without error
            dal.save_documents(doc_chunk[:index_in_docs_chunk])
            _save_users_docs_current_state(users, user_docs_accumulator)
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


def _save_users_docs_current_state(users, user_docs_accumulator):
    lrn_users_docs = user_docs_accumulator.build_user_docs()
    user_to_user_docs = (
        (user, [UserDocument(lrn_user_doc.doc_id, lrn_user_doc.grade) for lrn_user_doc in lrn_user_docs])
        for user, lrn_user_docs in zip(users, lrn_users_docs)
    )
    dal.save_users_docs(user_to_user_docs)
