#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import subprocess32 as subprocess
from server.dal import Dal
from server.frontendstructs import FeatureSet, TopicModelDescription
import server.structinit as structinit


class LaunchScrapAndLearnTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()
        # current model settings to prevent long model update
        model_id = '3206b8699d6040f7d46d0b72eb4532801629397cf96f21137611746537aacf31'
        nb_topics = 500
        model = TopicModelDescription.make_from_scratch(model_id, [[]])
        self.dal.topic_model.save(model)
        ref_feature_set_id = 'LaunchScrapAndLearnTests_ref_feature_set_id'
        self.dal.feature_set.save_feature_set(FeatureSet.make_from_scratch(
            ref_feature_set_id, ['feature_' + str(i) for i in range(nb_topics)], model_id))
        self.dal.feature_set.save_ref_feature_set_id(ref_feature_set_id)
        self.is_coverage = bool(os.environ.get('COVERAGE', None))

    def test_launch_scrap_and_learn(self):
        user_name = 'test_launch_scrap_and_learn'
        nb_docs = str(10)
        user = structinit.create_user_in_db(user_name, [], 'pass', self.dal)
        directory = os.path.dirname(os.path.abspath(__file__))
        root_dir = directory + '/../..'

        if not self.is_coverage:
            docker_image_name = "scrap_learn"
            model_directory_in_docker_image = "trained_topic_model"
            cassette_path_in_docker_image = "src/functests/vcr_cassettes/test_launch_scrap_and_learn.yaml"
            local_datastore = "http://localhost:33001"

            subprocess.call(["tools/build_docker_scrap_learn.sh"], cwd=root_dir, shell=True)
            subprocess.call(['docker', 'run',
                             "--net=host",  # so container can access local datastore address
                             "-e", "TEST_ENV=True",
                             "-e", "DATASTORE_HOST=" + local_datastore,
                             docker_image_name,
                             model_directory_in_docker_image,
                             cassette_path_in_docker_image,
                             user_name,
                             nb_docs])
        else:
            import sys
            from orchestrator.scrap_and_learn import scrap_and_learn
            cassette_file = directory + '/vcr_cassettes/test_launch_scrap_and_learn.yaml'
            model_dir = root_dir + '/docker_images/gator_deps/trained_topic_model'
            sys.argv = [None, model_dir, cassette_file, user_name, nb_docs]
            scrap_and_learn()

        user_docs = self.dal.user_doc.get_users_docs([user])[0]
        self.assertTrue(len(user_docs) > 6)  # some docs are filtered because not classified
        sorted_docs = sorted(user_docs, key=lambda u: u.grade, reverse=True)
        for doc in sorted_docs[:3]:  # the first user docs should have a significant value
            self.assertTrue(doc.grade > 0.05)


if __name__ == '__main__':
    unittest.main()
