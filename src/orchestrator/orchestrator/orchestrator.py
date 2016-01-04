#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import datetime
import logging
from time import sleep
import jsonpickle

from learner.learner import compute_user_doc_matching
from scraper.scraper import scrap
from server.frontendstructs import Document
import server.dal as dal
from topicmodeller.topicmodeller import TopicModeller, classify


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


def orchestrate(scraper_output_folder, tm_data_folder, tm_output_folder):
    _setup_env()

    topic_modeller = TopicModeller()
    topic_modeller.load(tm_data_folder)

    # TODO Get users pylint: disable=fixme
    users = dal.get_all_users()
    users_feature_vectors = dal.get_users_feature_vectors(users)  # pylint: disable=unused-variable
    users_docs = dal.get_user_docs(users)  # pylint: disable=unused-variable

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

                # Classify the document
                topic_modeller_document = classify(topic_modeller, scraper_document)
                # Dump topic modeller document
                _dump_as_json_document(topic_modeller_document, folder=tm_output_folder)

                doc = Document.make_from_scratch( # pylint: disable=unused-variable
                    topic_modeller_document.url, topic_modeller_document.title, summary=None)
                # TODO Save document in DB pylint: disable=fixme

                user_doc_matching_by_user = compute_user_doc_matching(  # pylint: disable=unused-variable
                    user_feature_vectors=user_feature_vectors,
                    document_feature_vector=[topic_value for (_, topic_value) in topic_modeller_document.topics],
                    min_grade=0.9)

                # TODO Save the updated user in DB (return only updated users ?) pylint: disable=fixme

        except Exception as exception: # pylint: disable=broad-except
            logging.error("The orchestrator crashed! Starting it over ...")
            logging.exception(exception)
            sleep(30)
