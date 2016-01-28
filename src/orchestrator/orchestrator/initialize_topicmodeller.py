#!/usr/bin/env python
# -*- coding: utf-8 -*-

import server.dal as dal


def initialize_topicmodeller_and_db(topic_modeller, html_documents, tm_data_folder, num_topics):
    initialize_topicmodeller(topic_modeller, html_documents, tm_data_folder, num_topics)
    initialize_db(topic_modeller)


def initialize_topicmodeller(topic_modeller, html_documents, tm_data_folder, num_topics):
    topic_modeller.initialize(html_documents, num_topics)
    topic_modeller.save(tm_data_folder)


def initialize_db(topic_modeller):
    feature_names = [words[0] for (_, words) in topic_modeller.topics]
    dal.save_features(dal.REF_FEATURE_SET, feature_names)
