#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from orchestrator.updatemodel import update_model_in_db
import server.frontendstructs as struct
from server.dal import Dal


class MockTopicModel(object):

    def __init__(self):
        self.model_id = 'new_model_id'
        self.topics = [
            [('word', 0.5)],
            [('other_topic', 1.0)]
        ]


class UpdateModelTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()

    def test_update_model_in_db(self):
        # 1) save input in datastore
        topics = [[('word', 1.0)]]
        model_id = 'previous_model_id'
        model = struct.TopicModelDescription.make_from_scratch(model_id, topics)
        self.dal.topic_model.save(model)

        feature_set_id = 'feature_set_id_test_update_model_in_db'
        self.dal.feature_set.save_feature_set(struct.FeatureSet.make_from_scratch(feature_set_id, ['feat_name'], model_id))

        vec_doc = [0.8]
        feat_vec_doc = struct.FeatureVector.make_from_scratch(vec_doc, feature_set_id)
        url_hash = 'hash_test_update_model_in_db'
        doc = struct.Document.make_from_scratch('', url_hash, None, None, feat_vec_doc)
        self.dal.doc.save_documents([doc])

        email = 'email_test_update_model_in_db'
        user = struct.User.make_from_scratch(email, '')
        self.dal.user.save_user(user, 'password')

        vec_profile = [-1]
        feat_vec_profile = struct.FeatureVector.make_from_scratch(vec_profile, feature_set_id)
        explicit = [2.0]
        positive = [3.0]
        negative = [4.0]
        pos_sum = 1.0
        neg_sum = 2.0
        model_data = struct.UserProfileModelData.make_from_scratch(explicit, positive, negative, pos_sum, neg_sum)
        profile = struct.UserComputedProfile.make_from_scratch(feat_vec_profile, model_data)
        self.dal.user_computed_profile.save_user_computed_profile(user, profile)
        profile = self.dal.user_computed_profile.get_user_computed_profiles([user])[0]  # to update profile.datetime

        user_doc = struct.UserDocument.make_from_scratch(doc, 0.0)
        self.dal.user_doc.save_user_docs(user, [user_doc])

        # 2) call update
        mock_model = MockTopicModel()
        update_model_in_db(mock_model, [user])

        # 3) check datastore updates
        new_model_id = 'new_model_id'
        new_model = self.dal.topic_model.get(new_model_id)
        self.assertIsNotNone(new_model)

        new_feature_set = self.dal.feature_set.get_feature_set(new_model_id)
        self.assertIsNotNone(new_feature_set)

        updated_doc = self.dal.doc.get_doc(url_hash)
        self.assertEquals(new_model_id, updated_doc.feature_vector.feature_set_id)
        self.assertEquals([vec_doc[0] * 2, 0.0], updated_doc.feature_vector.vector)  # because weight on 'word' divided by 2

        updated_profile = self.dal.user_computed_profile.get_user_computed_profiles([user])[0]
        self.assertEquals(profile.datetime, updated_profile.datetime)
        updated_profile_feat_vec = updated_profile.feature_vector
        self.assertEquals(new_model_id, updated_profile_feat_vec.feature_set_id)
        self.assertEquals([1.0, 0.0], updated_profile_feat_vec.vector)  # because no weight on 2nd topic and normalized

        updated_model_data = updated_profile.model_data
        self.assertEquals(pos_sum, updated_model_data.positive_feedback_sum_coeff)
        self.assertEquals(neg_sum, updated_model_data.negative_feedback_sum_coeff)
        self.assertEquals([explicit[0] * 2, 0.0], updated_model_data.explicit_feedback_vector)
        self.assertEquals([positive[0] * 2, 0.0], updated_model_data.positive_feedback_vector)
        self.assertEquals([negative[0] * 2, 0.0], updated_model_data.negative_feedback_vector)


if __name__ == '__main__':
    unittest.main()
