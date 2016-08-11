#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import numpy as np
from server.dal import Dal
import server.frontendstructs as struct
from learner.userprofiler import UserProfile
from orchestrator.userprofileupdater import update_profiles_in_database


class MockUserProfiler(object):
    def __init__(self, feedback_vector):
        self._feedback_vector = feedback_vector

    def compute_user_profile(self, previous_model_data, previous_datetime, actions_on_docs, new_datetime): # pylint: disable=unused-argument
        return UserProfile(struct.UserProfileModelData.make_empty(len(self._feedback_vector)), self._feedback_vector)


class UserProfileBuilderTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()

    def test_update_all_user_profiles_in_database(self):
        user1 = struct.User.make_from_scratch(email='user1-test_update_user_profiles_in_database', interests=['interests1'])
        user2 = struct.User.make_from_scratch(email='user2-test_update_user_profiles_in_database', interests=['interests2'])
        self.dal.save_user(user1, 'password1')
        self.dal.save_user(user2, 'password2')

        feature_set_id = 'test_update_user_profiles_in_database'
        self._build_feature_set(feature_set_id)

        doc = self._build_doc(feature_set_id)
        self.dal.save_documents([doc])

        profile1 = self._build_profile(feature_set_id, [2.0, 2.0])
        self.dal.save_computed_user_profile(user1, profile1)

        self.dal.save_user_action_on_doc(user1, doc, struct.UserActionTypeOnDoc.up_vote)  # should be used because after save
        self.dal.save_user_action_on_doc(user2, doc, struct.UserActionTypeOnDoc.up_vote)  # should not be used

        profile2 = self._build_profile(feature_set_id, [2.0, 2.0])
        self.dal.save_computed_user_profile(user2, profile2)

        # identical action
        self.dal.save_user_action_on_doc(user1, doc, struct.UserActionTypeOnDoc.down_vote)
        self.dal.save_user_action_on_doc(user2, doc, struct.UserActionTypeOnDoc.down_vote)

        update_profiles_in_database()

        profiles = self.dal.get_user_computed_profiles([user1, user2])

        # User 1 should prefer doc more than user 2. Doc feature vector is confounded with "x-axis", user 1 new feature
        # vector angle should thus be closest to x-axis than user 2 feature vector.
        self.assertLess(np.arctan2(profiles[0].feature_vector.vector[1], profiles[0].feature_vector.vector[0]),
                        np.arctan2(profiles[1].feature_vector.vector[1], profiles[1].feature_vector.vector[0]))

        # Initial feature vector should not change
        self.assertEquals(profile1.initial_feature_vector.vector, profiles[0].initial_feature_vector.vector)
        self.assertEquals(profile2.initial_feature_vector.vector, profiles[1].initial_feature_vector.vector)

    def test_feat_vec_at_mid_ang_between_init_feat_vec_and_profiler_vec(self):
        user = struct.User.make_from_scratch(email='user-test_feat_vec_at_mid_ang_between_init_feat_vec_and_profiler_vec',
                                             interests=['interests'])
        self.dal.save_user(user, 'password')

        feature_set_id = 'test_feat_vec_at_mid_ang_between_init_feat_vec_and_profiler_vec'
        self._build_feature_set(feature_set_id)

        profile = self._build_profile(feature_set_id, [0.0, 2.0])
        self.dal.save_computed_user_profile(user, profile)

        update_profiles_in_database(MockUserProfiler([1.0, 0.0]))

        profiles = self.dal.get_user_computed_profiles([user])

        # As profiler vector and user initial feature vector are orthogonal, profiler vector is at pi/2 rad and initial
        # feature vector at 0 rad, the new feature vector should be at pi/4 rad (which the angle of the vector [0.5, 0.5]).
        self.assertEquals(np.arctan2(profiles[0].feature_vector.vector[1], profiles[0].feature_vector.vector[0]),
                          np.arctan2(0.5, 0.5))

        self.assertEquals(profile.initial_feature_vector.vector, profiles[0].initial_feature_vector.vector)

    def _build_feature_set(self, feature_set_id):
        self.dal.save_features(feature_set_id, ['feature_name1', 'feature_name2'])
        return feature_set_id

    @staticmethod
    def _build_doc(feature_set_id):
        feature_vector = struct.FeatureVector.make_from_scratch([1.0, 0], feature_set_id)
        doc = struct.Document.make_from_scratch('u1', 't1', 's1', feature_vector)
        return doc

    @staticmethod
    def _build_profile(feature_set_id, init_feat_vec_values):
        initial_feature_vector = struct.FeatureVector.make_from_scratch(init_feat_vec_values, feature_set_id)
        feature_vector = struct.FeatureVector.make_from_scratch([1.0, 1.0], feature_set_id)
        model_data = struct.UserProfileModelData.make_empty(2)
        return struct.UserComputedProfile.make_from_scratch(initial_feature_vector, feature_vector, model_data)


if __name__ == '__main__':
    unittest.main()
