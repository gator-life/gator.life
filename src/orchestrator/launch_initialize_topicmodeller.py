#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common.JsonDocLoader import JsonDocLoader
from common.remote_api import initialize_remote_api
from topicmodeller.topicmodeller import TopicModeller
from orchestrator.initialize_topicmodeller import initialize_topicmodeller

import jsonpickle
import logging
import os


logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,
                    filename='initialize_model.log')


class RepeatableHtmlDocuments(object):
    def __init__(self, folder):
        self.doc_loader = JsonDocLoader(folder)

    def __iter__(self):
        for scraper_document in self.doc_loader:
            yield scraper_document.html_content


initialize_remote_api()

html_documents = RepeatableHtmlDocuments('/home/mohamed/Development/Data/gator/DocsLight')

initialize_topicmodeller(TopicModeller.make(), html_documents, tm_data_folder='/home/mohamed/Development/Data/gator/TM')
