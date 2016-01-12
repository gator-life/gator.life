#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topicmodeller.topicmodeller import TopicModeller

import jsonpickle
import logging
import os


logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,
                    filename='tm_initialize_model.log')


class RepeatableHtmlDocuments(object):
    def __init__(self, folder):
        self.folder = folder

    def __iter__(self):
        for file_name in os.listdir(self.folder):
            file_path = os.path.join(self.folder, file_name)
            file_content = open(file_path).read()

            scraper_document = jsonpickle.decode(file_content)
            yield scraper_document.html_content


html_documents = RepeatableHtmlDocuments('/home/mohamed/Development/Data/gator/Scraping_11-01-2016')

topic_modeller = TopicModeller.make()
topic_modeller.initialize(html_documents, num_topics=128)
topic_modeller.save('/home/mohamed/Development/Data/gator/TopicModellerData')
