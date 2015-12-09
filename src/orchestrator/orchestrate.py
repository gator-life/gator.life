#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from orchestrator.orchestrator import orchestrate


logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO, ilename='orchestrator.log')


orchestrate(scraper_output_folder='/home/mohamed/Development/Data/gator/orchestrate/scraper_json/',
            tm_data_folder='/home/mohamed/Development/Data/TopicModelling/data',
            tm_output_folder='/home/mohamed/Development/Data/gator/orchestrate/topicmodeller_json/')
