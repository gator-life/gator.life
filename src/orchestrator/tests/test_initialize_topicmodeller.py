#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from orchestrator.initialize_topicmodeller import initialize_topicmodeller_and_db
import server.dal as dal


class MockTopicModeller(object):
    def __init__(self, topics):
        self.topics = topics
        self.initialized = False
        self.saved = False

    def initialize(self, html_documents, num_topics): # pylint: disable=unused-argument
        self.initialized = True

    def save(self, tm_data_folder): # pylint: disable=unused-argument
        self.saved = True


class TopicModellerTests(unittest.TestCase):
    def test_initialize_topicmodeller(self):
        features_names = [str(i) for i in range(128)]
        topics = [(0, [feature]) for feature in features_names]

        topic_modeller = MockTopicModeller(topics)
        initialize_topicmodeller_and_db(topic_modeller, [], '')

        self.assertTrue(topic_modeller.initialized)
        self.assertTrue(topic_modeller.saved)

        saved_features_names = dal.get_features(dal.REF_FEATURE_SET)
        self.assertEquals(saved_features_names, features_names)


if __name__ == '__main__':
    unittest.main()
