#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import subprocess32 as subprocess
from server.environment import IS_DEV_ENV, IS_COVERAGE
from server.dal import Dal
from server.frontendstructs import FeatureSet, TopicModelDescription
from server.structinit import UserCreator


class BackgroundUpdateTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()
        # current model settings to prevent long model update
        model_id = '3206b8699d6040f7d46d0b72eb4532801629397cf96f21137611746537aacf31'
        nb_topics = 500
        model = TopicModelDescription.make_from_scratch(model_id, [[('w' + str(i), 1)] for i in range(nb_topics)])
        self.dal.topic_model.save(model)
        ref_feature_set_id = 'BackgroundUpdateTests_ref_feature_set_id'
        self.dal.feature_set.save_feature_set(FeatureSet(
            ref_feature_set_id, ['feature_' + str(i) for i in range(nb_topics)], model_id))
        self.dal.feature_set.save_ref_feature_set_id(ref_feature_set_id)
        self.bypass_docker = IS_DEV_ENV or IS_COVERAGE

    def test_update_model_profiles_userdocs(self):
        user_name = 'test_launch_scrap_and_learn'
        nb_docs = str(9)

        interests = [' w' + str(i) for i in range(200)]  # choose 200 of the 500 words used in topic model description
        user = UserCreator().create_user_in_db(user_name, interests, 'pass', self.dal)

        directory = os.path.dirname(os.path.abspath(__file__))
        root_dir = directory + '/../..'

        if not self.bypass_docker:
            docker_image_name = "background_update"
            model_directory_in_docker_image = "trained_topic_model"
            cassette_path_in_docker_image = "src/functests/vcr_cassettes/update_model_profiles_userdocs.yaml"

            subprocess.call(["scripts/build_docker_background_update.sh"], cwd=root_dir, shell=True)
            subprocess.call(['docker', 'run',
                             "--net=host",  # so container can access local datastore address
                             "-e", "TEST_ENV=" + os.environ["TEST_ENV"],  # forward some environment variables
                             "-e", "DATASTORE_EMULATOR_HOST=" + os.environ["DATASTORE_EMULATOR_HOST"],
                             docker_image_name,
                             model_directory_in_docker_image,
                             cassette_path_in_docker_image,
                             user_name,
                             nb_docs])
        else:
            import sys
            from orchestrator.backgroundupdate import update_model_profiles_userdocs
            cassette_file = directory + '/vcr_cassettes/update_model_profiles_userdocs.yaml'
            model_dir = root_dir + '/docker_images/gator_deps/trained_topic_model'
            sys.argv = [None, model_dir, cassette_file, user_name, nb_docs]
            update_model_profiles_userdocs()

        user_docs = self.dal.user_doc.get_users_docs([user])[0]
        self.assertTrue(len(user_docs) > 6)  # some docs are filtered because not classified
        sorted_docs = sorted(user_docs, key=lambda u: u.grade, reverse=True)
        for doc in sorted_docs[:3]:  # the first user docs should have a significant value
            self.assertTrue(doc.grade > 0.05)


if __name__ == '__main__':
    unittest.main()
