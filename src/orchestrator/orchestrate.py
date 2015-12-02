#!/usr/bin/env python
# -*- coding: utf-8 -*-

from orchestrator.orchestrator import orchestrate


orchestrate(scraper_output_folder='/home/mohamed/Development/Data/gator/orchestrate/scraper_json/',
            tm_data_folder='/home/mohamed/Development/Data/TopicModelling/data',
            tm_output_folder='/home/mohamed/Development/Data/gator/orchestrate/topicmodeller_json/')
