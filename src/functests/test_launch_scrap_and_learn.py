#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import os
from server.dal import Dal, REF_FEATURE_SET
import server.structinit as structinit
from orchestrator.scrap_and_learn import scrap_and_learn


class LaunchScrapAndLearnTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()
        nb_topics_trained_model = 500
        self.dal.save_features(REF_FEATURE_SET, ['feature_' + str(i) for i in range(0, nb_topics_trained_model)])

    def test_launch_scrap_and_learn(self):
        directory = os.path.dirname(os.path.abspath(__file__))
        cassette_file = directory + '/vcr_cassettes/test_launch_scrap_and_learn.yaml'
        root_dir = directory + '/../..'
        model_dir = root_dir + '/resources/trained_topic_model'
        user_name = 'test_launch_scrap_and_learn'
        sys.argv = [None, model_dir, cassette_file, user_name, 10]
        user = structinit.create_user_in_db(user_name, [], 'pass', self.dal)
        scrap_and_learn()
        user_docs = self.dal.get_users_docs([user])[0]
        self.assertTrue(len(user_docs) > 6)  # some docs are filtered because not classified
        sorted_docs = sorted(user_docs, key=lambda u: u.grade, reverse=True)
        for doc in sorted_docs[:3]:  # the first user docs should have a significant value
            self.assertTrue(doc.grade > 0.05)


if __name__ == '__main__':
    unittest.main()
