#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from common.datehelper import utcnow
from server.structinit import UserCreator, _ProfileInitializer, _get_user_docs
from server.dal import Dal
from server.frontendstructs import FeatureSet, TopicModelDescription, Document, FeatureVector


def make_doc(vector, feature_set_id, url_hash):
    feat_vec = FeatureVector(vector, feature_set_id)
    doc = Document('u', url_hash, '', '', feat_vec)
    return doc


class UserCreatorTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()

    def _save_dummy_feature_set(self, feature_set_id):
        model_id = 'UserCreatorTests_save_dummy_feature_set_model_id'
        self.dal.feature_set.save_feature_set(
            FeatureSet(feature_set_id, feature_names=['f1, f2'], model_id=model_id))
        self.dal.feature_set.save_ref_feature_set_id(feature_set_id)
        self.dal.topic_model.save(TopicModelDescription.make_from_scratch(model_id, [
            [('w1', 1)],
            [('w2', 1)]
        ]))

    def test_create_user_in_db(self):
        user_id = 'user_id_test_create_user_in_db'
        interests = ['w1', 'w2']
        ref_feature_set_id = 'test_create_user_in_db'

        self._save_dummy_feature_set(ref_feature_set_id)
        doc = make_doc([1, 1], ref_feature_set_id, 'url_test_create_user_in_db')
        self.dal.doc.save_documents([doc])
        user_creator = UserCreator()
        user = user_creator.create_user_in_db(user_id, interests, self.dal)

        user_from_db = self.dal.user.get_user(user_id)
        profile = self.dal.user_computed_profile.get_user_computed_profiles([user])[0]

        self.assertEquals(user_id, user.user_id)
        self.assertEquals(user_id, user_from_db.user_id)
        self.assertEquals(interests, user.interests)
        self.assertEquals(interests, user_from_db.interests)
        self.assertEquals(ref_feature_set_id, profile.feature_vector.feature_set_id)
        self.assertEqual(1, len(self.dal.user_doc.get_user_docs(user)))

    def test_get_user_docs(self):
        ref_feature_set_id = 'test_get_user_docs_ref_feature_set_id'
        self._save_dummy_feature_set(ref_feature_set_id)
        doc_before = make_doc([1, 0.1], ref_feature_set_id, 'u_before')

        self.dal.doc.save_documents([doc_before])
        date_min = utcnow()

        doc_low = make_doc([0.3, 0.7], ref_feature_set_id, 'url_low')
        doc_high = make_doc([0.7, 0.3], ref_feature_set_id, 'url_high')
        doc_bad = make_doc([0.9, 0.1], 'bad_set_id', 'url_bad_det')

        self.dal.doc.save_documents([doc_low, doc_high, doc_bad])
        feat_user = FeatureVector([1, 0], ref_feature_set_id)
        user_docs = _get_user_docs(self.dal, feat_user, date_min, 1)
        self.assertEqual(1, len(user_docs))
        self.assertEqual('url_high', user_docs[0].document.url_hash)


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
        self.assertEquals([0, 0], model_data.negative_feedback_vector)
        self.assertEquals(2, len(explicit_vec))
        self.assertTrue(explicit_vec[1] > explicit_vec[0] > 0)
        self.assertEquals(explicit_vec[1] / explicit_vec[0], feature_vec.vector[1] / feature_vec.vector[0])
        self.assertEquals(feature_vec.feature_set_id, ref_feature_set_id)


if __name__ == '__main__':
    unittest.main()
