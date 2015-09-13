#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topicmodeller.topicmodeller import RepeatableBatchedDocuments, TopicModeller, TopicModellerDocument

import codecs
import datetime
import jsonpickle
import logging
import os


logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,
                    filename='tm_classify.log')


def classify_and_dump_json(tm, documents, output_folder):
    jsonpickle.set_encoder_options('simplejson', indent=4, ensure_ascii=False)

    tm_documents = (TopicModellerDocument(scraper_document.link_element.url, tm.classify(document))
                    for (batched_scraper_documents, batched_documents) in documents
                    for (scraper_document, document) in zip(batched_scraper_documents, batched_documents))

    date = datetime.datetime.utcnow()

    for (i, tm_document) in enumerate(tm_documents):
        json = jsonpickle.encode(tm_document)
        filename = os.path.join(output_folder, str(date) + '_' + str(i) + '.json')
        with codecs.open(filename=filename, mode='w', encoding='utf-8') as file_desc:
            file_desc.write(json)


documents = RepeatableBatchedDocuments('/home/mohamed/Development/Data/TopicModelling/recorded_html_01_08', 2000)

tm = TopicModeller('/home/mohamed/Development/Data/TopicModelling/data', 128)

classify_and_dump_json(tm, documents, '/home/mohamed/Development/Data/TopicModelling/json')