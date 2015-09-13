#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topicmodeller.topicmodeller import TopicModeller, RepeatableBatchedDocuments

import logging

logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,
                    filename='tm_initialize_model.log')

documents = RepeatableBatchedDocuments('/home/mohamed/Development/Data/TopicModelling/recorded_html_01_08', 2000)

tm = TopicModeller('/home/mohamed/Development/Data/TopicModelling/data', 128)

tm.initialize_dictionary(documents)
tm.feed(documents)