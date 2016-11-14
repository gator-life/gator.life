#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from server.structinit import UserCreator, _ProfileInitializer
from server.dal import Dal
from server.frontendstructs import FeatureSet, TopicModelDescription
import common.crypto as crypto


class UserCreatorTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()

    def test_create_user_in_db(self):
        email = 'email_test_create_user_in_db'
        interests = ['test_create_user_in_db_interest1', 'test_create_user_in_db_interest2']
        password = 'password_test_create_user_in_db'
        ref_feature_set_id = 'test_create_user_in_db'
        model_id = 'test_create_user_in_db_model_id'
        self.dal.feature_set.save_feature_set(
            FeatureSet.make_from_scratch(ref_feature_set_id, feature_names=['f1', 'f2', 'f3'], model_id=model_id))
        self.dal.feature_set.save_ref_feature_set_id(ref_feature_set_id)
        self.dal.topic_model.save(TopicModelDescription.make_from_scratch(model_id, [[('w', 1)]]))
        user_creator = UserCreator()
        user = user_creator.create_user_in_db(email, interests, password, self.dal)

        user_from_db, hash_password_from_db = self.dal.user.get_user_and_hash_password(email)
        profile = self.dal.user_computed_profile.get_user_computed_profiles([user])[0]

        self.assertEquals(email, user.email)
        self.assertEquals(email, user_from_db.email)
        self.assertEquals(interests, user.interests)
        self.assertEquals(interests, user_from_db.interests)
        self.assertTrue(crypto.verify_password(password, hash_password_from_db))
        self.assertEquals(ref_feature_set_id, profile.feature_vector.feature_set_id)


class ProfileInitializerTests(unittest.TestCase):

    def test_get_new_profile(self):
        ref_feature_set_id = 'test_get_new_profile_ref_feature_set_id'
        topics = [
            [('t1_w1', 0.8), ('t1_w2', 0.2)],
            [('t2_w1', 1.0)]
        ]
        model_description = TopicModelDescription.make_from_scratch('model_id', topics)
        initializer = _ProfileInitializer(ref_feature_set_id, model_description)
        interests = ['t1_w2, t2_w1.', ' useless_word']
        profile = initializer.get_new_profile(interests)
        model_data = profile.model_data
        feature_vec = profile.feature_vector
        explicit_vec = model_data.explicit_feedback_vector
        self.assertEquals(0, model_data.positive_feedback_sum_coeff)
        self.assertEquals(0, model_data.negative_feedback_sum_coeff)
        self.assertEquals([0, 0], model_data.positive_feedback_vector)
        self.assertEquals([0, 0], model_data.positive_feedback_vector)
        self.assertEquals(2, len(explicit_vec))
        self.assertTrue(explicit_vec[1] > explicit_vec[0] > 0)
        self.assertEquals(explicit_vec[1] / explicit_vec[0], feature_vec.vector[1] / feature_vec.vector[0])
        self.assertEquals(feature_vec.feature_set_id, ref_feature_set_id)


if __name__ == '__main__':
    unittest.main()
