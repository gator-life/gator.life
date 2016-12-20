#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from orchestrator.updatemodel import ModelUpdater
import server.frontendstructs as struct
from server.dal import Dal


class MockTopicModel(object):

    @staticmethod
    def get_model_id():
        return 'new_model_id'

    @staticmethod
    def get_topics():
        return [
            [('word', 0.5)],
            [('other_topic', 1.0)]
        ]


class EmptyTopicModel(object):

    @staticmethod
    def get_model_id():
        return 'test_update_model_in_db_with_model_already_ref_do_nothing'

    @staticmethod
    def get_topics():
        raise ValueError("should not be called")


class ModelUpdaterTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()

    def test_update_model_in_db_with_model_already_ref_do_nothing(self):
        model = EmptyTopicModel()
        model_id = model.get_model_id()
        feature_set_id = 'test_update_model_in_db_with_model_already_ref_do_nothing_feature_set_id'
        self.dal.feature_set.save_feature_set(struct.FeatureSet(feature_set_id, ['feat'], model_id))
        self.dal.feature_set.save_ref_feature_set_id(feature_set_id)
        updater = ModelUpdater()
        # would fail in EmptyTopicModel.get_topics() if function tried to update model in database
        updater.update_model_in_db(model, None)

    def test_update_model_in_db(self):
        # 1) save input in datastore
        topics = [[('word', 1.0)]]
        model_id = 'previous_model_id'
        model = struct.TopicModelDescription.make_from_scratch(model_id, topics)
        self.dal.topic_model.save(model)
        feature_set_id = 'feature_set_id_test_update_model_in_db'
        self.dal.feature_set.save_ref_feature_set_id(feature_set_id)
        self.dal.feature_set.save_feature_set(struct.FeatureSet(feature_set_id, ['feat_name'], model_id))

        vec_doc = [0.8]
        url_hash = 'hash_test_update_model_in_db'
        doc = self._get_saved_doc(feature_set_id, url_hash, vec_doc)

        user = struct.User.make_from_scratch('email_test_update_model_in_db', '')
        self.dal.user.save_user(user, 'password')

        vec_profile = [-1]
        explicit = [2.0]
        positive = [3.0]
        negative = [4.0]
        pos_sum = 1.0
        neg_sum = 2.0
        profile = self._get_saved_profile(user, vec_profile, feature_set_id, explicit, positive, negative, pos_sum, neg_sum)

        user_doc = struct.UserDocument(doc, 0.0)
        self.dal.user_doc.save_user_docs(user, [user_doc])

        # 2) call update
        mock_topic_model = MockTopicModel()
        ModelUpdater().update_model_in_db(mock_topic_model, [user])

        # 3) check datastore updates
        new_model_expected_id = mock_topic_model.get_model_id()
        new_ref_feature_set_id = self.dal.feature_set.get_ref_feature_set_id()
        self.assertEquals(new_model_expected_id, new_ref_feature_set_id)
        new_model = self.dal.topic_model.get(new_model_expected_id)
        self.assertIsNotNone(new_model)

        new_feature_set = self.dal.feature_set.get_feature_set(new_model_expected_id)
        self.assertEquals(new_feature_set.model_id, new_model_expected_id)
        self.assertEquals(['word', 'other_topic'], new_feature_set.feature_names)
        self.assertEquals(new_model_expected_id, new_feature_set.model_id)

        updated_doc = self.dal.doc.get_doc(url_hash)
        self.assertEquals(doc.datetime, updated_doc.datetime)
        self.assertEquals(new_ref_feature_set_id, updated_doc.feature_vector.feature_set_id)
        self.assertEquals([vec_doc[0] * 2, 0.0], updated_doc.feature_vector.vector)  # because weight on 'word' divided by 2

        updated_profile = self.dal.user_computed_profile.get_user_computed_profiles([user])[0]
        self.assertEquals(profile.datetime, updated_profile.datetime)
        updated_profile_feat_vec = updated_profile.feature_vector
        self.assertEquals(new_ref_feature_set_id, updated_profile_feat_vec.feature_set_id)
        self.assertEquals([1.0, 0.0], updated_profile_feat_vec.vector)  # because no weight on 2nd topic and normalized

        updated_model_data = updated_profile.model_data
        self.assertEquals(pos_sum, updated_model_data.positive_feedback_sum_coeff)
        self.assertEquals(neg_sum, updated_model_data.negative_feedback_sum_coeff)
        self.assertEquals([explicit[0] * 2, 0.0], updated_model_data.explicit_feedback_vector)
        self.assertEquals([positive[0] * 2, 0.0], updated_model_data.positive_feedback_vector)
        self.assertEquals([negative[0] * 2, 0.0], updated_model_data.negative_feedback_vector)

    def _get_saved_doc(self, feature_set_id, url_hash, vec_doc):
        feat_vec_doc = struct.FeatureVector(vec_doc, feature_set_id)
        doc = struct.Document('', url_hash, None, None, feat_vec_doc)
        self.dal.doc.save_documents([doc])
        doc = self.dal.doc.get_doc(url_hash)  # to update doc.datetime
        return doc

    def _get_saved_profile(self, user, vec_profile, feature_set_id, explicit, positive, negative, pos_sum, neg_sum):  # pylint: disable=too-many-arguments
        # (disable pylint, nb of args here seems good trade-off)
        feat_vec_profile = struct.FeatureVector(vec_profile, feature_set_id)
        model_data = struct.UserProfileModelData.make_from_scratch(explicit, positive, negative, pos_sum, neg_sum)
        profile = struct.UserComputedProfile(feat_vec_profile, model_data)
        self.dal.user_computed_profile.save_user_computed_profile(user, profile)
        profile = self.dal.user_computed_profile.get_user_computed_profiles([user])[0]  # to update profile.datetime
        return profile


if __name__ == '__main__':
    unittest.main()
