#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topicmodeller.topicmodeller import classify_and_dump_json

import logging


logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,
                    filename='tm_classify.log')

classify_and_dump_json(documents_folder='/home/mohamed/Development/Data/TopicModelling/recorded_html_01_08',
                       tm_data_folder='/home/mohamed/Development/Data/TopicModelling/data',
                       output_folder='/home/mohamed/Development/Data/TopicModelling/json')
