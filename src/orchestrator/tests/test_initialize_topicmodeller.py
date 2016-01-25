#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from orchestrator.initialize_topicmodeller import initialize_topicmodeller
import server.dal as dal


class MockTopicModeller(object):
    def __init__(self, topics):
        self.topics = topics

    def initialize(self, html_documents, num_topics):
        pass

    def save(self, tm_data_folder):
        pass


class TopicModellerTests(unittest.TestCase):
    def test_initialize_topicmodeller(self):
        features_names = [str(i) for i in range(128)]
        topics = [(0, [feature]) for feature in features_names]

        initialize_topicmodeller(MockTopicModeller(topics), [], '')

        saved_features_names = dal.get_features(dal.REF_FEATURE_SET)
        self.assertEquals(saved_features_names, features_names)


if __name__ == '__main__':
    unittest.main()
