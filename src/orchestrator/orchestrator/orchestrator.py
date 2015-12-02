#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import datetime
import logging
from time import sleep
import jsonpickle

from learner.learner import learn_for_users
from scraper.scraper import scrap
from server.frontendstructs import Document
from topicmodeller.topicmodeller import TopicModeller, classify


logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO, ilename='orchestrator.log')


def _to_json(document):
    # set unicode and pretty-print
    jsonpickle.set_encoder_options('simplejson', indent=4, ensure_ascii=False)
    return jsonpickle.encode(document)


def _dump_json_document(document, folder):
    json = _to_json(document)
    filename = folder + '/' + str(datetime.datetime.utcnow()) + '.json'
    with codecs.open(filename=filename, mode='w', encoding='utf-8') as file_desc:
        file_desc.write(json)


def orchestrate(scraper_output_folder, tm_data_folder, tm_output_folder):
    topicmodeller = TopicModeller()
    topicmodeller.load(tm_data_folder)

    # TODO Get users pylint: disable=fixme
    users = []

    # We need this high level loop to prevent crashes for whatever reason.
    #
    # For instance, exceptions are thrown by internal reddit generator, a generator cannot be continued after it raises an
    # exception, so we have to make another generator and restart The observed exception was due to a deficient connection.
    # We sleep to not flood logs (it won't come back immediately)
    while True:
        try:
            for scraper_document in scrap():
                # Dump scraper document
                _dump_json_document(scraper_document, folder=scraper_output_folder)

                # Classify the document
                topicmodeller_document = classify(topicmodeller, scraper_document)
                # Dump topic modeller document
                _dump_json_document(topicmodeller_document, folder=tm_output_folder)

                document = Document(topicmodeller_document.url, topicmodeller_document.title, db_key=None)
                # TODO Save document in DB pylint: disable=fixme

                # Learn for users
                learn_for_users(users, document, topicmodeller_document.topics, min_grade=0.5)

                # TODO Save the updated user in DB (return only updated users ?) pylint: disable=fixme

        except Exception as exception: # pylint: disable=broad-except
            logging.error("The orchestrator crashed! Starting it over ...")
            logging.exception(exception)
            sleep(30)
