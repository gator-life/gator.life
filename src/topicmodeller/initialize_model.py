#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topicmodeller.topicmodeller import initialize_model, _to_topicmodellable_document

import jsonpickle
import logging
import os


logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,
                    filename='tm_initialize_model.log')


class RepeatableScraperDocuments(object):
    def __init__(self, folder):
        self.folder = folder

    def __iter__(self):
        for file_name in os.listdir(self.folder):
            file_path = os.path.join(self.folder, file_name)
            file_content = open(file_path).read()

            yield jsonpickle.decode(file_content)


scraper_documents = RepeatableScraperDocuments('/home/mohamed/Development/Data/TopicModelling/recorded_html_01_08')

initialize_model(scraper_documents, tm_data_folder='/home/mohamed/Development/Data/TopicModelling/data', num_topics=128)
