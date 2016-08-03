#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from orchestrator.initialize_topicmodeller import initialize_topicmodeller_and_db
from server.dal import Dal, REF_FEATURE_SET


class MockTopicModeller(object):

    def __init__(self, topics, html_documents, tm_data_folder, num_topics):
        self.topics = topics

        self.expected_html_documents = html_documents
        self.expected_tm_data_folder = tm_data_folder
        self.expected_num_topics = num_topics

        self.initialized = False
        self.saved = False

    def initialize(self, html_documents, num_topics):
        self.initialized = (html_documents == self.expected_html_documents) and (num_topics == self.expected_num_topics)

    def save(self, tm_data_folder):
        self.saved = tm_data_folder == self.expected_tm_data_folder


class TopicModellerTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()

    def test_initialize_topicmodeller(self):
        num_topics = 128

        features_names = [str(i) for i in range(num_topics)]
        topics = [(0, [feature]) for feature in features_names]

        html_documents = ['doc1', 'doc2', 'doc2']
        tm_data_folder = 'save_path'

        topic_modeller = MockTopicModeller(topics, html_documents, tm_data_folder, num_topics)

        initialize_topicmodeller_and_db(topic_modeller, html_documents, tm_data_folder, num_topics)

        self.assertTrue(topic_modeller.initialized)
        self.assertTrue(topic_modeller.saved)

        saved_features_names = self.dal.get_features(REF_FEATURE_SET)
        self.assertEquals(saved_features_names, features_names)


if __name__ == '__main__':
    unittest.main()
