#!/usr/bin/env python
# -*- coding: utf-8 -*-

import server.dal as dal


def initialize_topicmodeller(topic_modeller, html_documents, tm_data_folder):
    topic_modeller.initialize(html_documents, num_topics=128)
    topic_modeller.save(tm_data_folder)

    feature_names = [words[0] for (_, words) in topic_modeller.topics]
    dal.save_features(dal.REF_FEATURE_SET, feature_names=feature_names)
