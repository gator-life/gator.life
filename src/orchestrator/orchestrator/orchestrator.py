#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import datetime
import logging
from time import sleep
import jsonpickle

import learner.learner as lrn
from scraper.scraper import scrap
from server.frontendstructs import Document, UserDocument
import server.dal as dal
from topicmodeller.topicmodeller import TopicModeller


def _setup_env():
    # set unicode and pretty-print
    jsonpickle.set_encoder_options('simplejson', indent=4, ensure_ascii=False)


def _to_json(document):
    return jsonpickle.encode(document)


def _dump_as_json_document(document, folder):
    json = _to_json(document)
    filename = folder + '/' + str(datetime.datetime.utcnow()) + '.json'
    with codecs.open(filename=filename, mode='w', encoding='utf-8') as file_desc:
        file_desc.write(json)


def orchestrate(scraper_output_folder, tm_data_folder):
    _setup_env()

    topic_modeller = TopicModeller.make()
    topic_modeller.load(tm_data_folder)

    users = dal.get_all_users()
    user_docs_accumulator = build_user_docs_accumulator(users)

    docs_chunk_size = 1000
    doc_chunk = [None]*docs_chunk_size
    index_in_docs_chunk = 0


    # We need this high level loop to prevent crashes for whatever reason.
    #
    # For instance, exceptions are thrown by internal reddit generator, a generator cannot be continued after it raises an
    # exception, so we have to make another generator and restart The observed exception was due to a deficient connection.
    # We sleep to not flood logs (it won't come back immediately)
    while True:
        try:
            for scraper_document in scrap():
                # Dump scraper document
                _dump_as_json_document(scraper_document, folder=scraper_output_folder)

                doc = Document.make_from_scratch(scraper_document.url, scraper_document.title, summary=None)
                doc_chunk[index_in_docs_chunk] = doc
                topic_feature_vector = topic_modeller.classify(scraper_document.html_content)
                user_docs_accumulator.add_doc(doc, topic_feature_vector)

                index_in_docs_chunk += 1
                if index_in_docs_chunk == docs_chunk_size:
                    index_in_docs_chunk = 0
                    dal.save_documents(doc_chunk)
                    save_users_docs_current_state(users, user_docs_accumulator)


        except Exception as exception: # pylint: disable=broad-except
            logging.error("The orchestrator crashed! Starting it over ...")
            logging.exception(exception)
            sleep(30)


def build_user_docs_accumulator(users):
    users_feature_vectors = dal.get_users_feature_vectors(users)
    users_docs = dal.get_users_docs(users)  # pylint: disable=unused-variable

    def build_learner_user_data(user_feature_vector, user_docs):
        learner_user_docs = (lrn.UserDoc(user_doc.document, user_doc.grade) for user_doc in user_docs)
        return lrn.UserData(user_feature_vector, learner_user_docs)

    user_data_list = (build_learner_user_data(vector, docs) for vector, docs in zip(users_feature_vectors, users_docs))
    user_docs_accumulator = lrn.UserDocumentsAccumulator(user_data_list, 30)
    return user_docs_accumulator


def save_users_docs_current_state(users, user_docs_accumulator):
    lrn_users_docs = user_docs_accumulator.build_user_docs()
    user_to_user_docs = (
        (user, [UserDocument(lrn_user_doc.doc_id, lrn_user_doc.grade) for lrn_user_doc in lrn_user_docs])
        for user, lrn_user_docs in zip(users, lrn_users_docs)
    )
    dal.save_users_docs(user_to_user_docs)
