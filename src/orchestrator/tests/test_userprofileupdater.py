#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import server.frontendstructs as struct
from server.dal import Dal
from orchestrator.userprofileupdater import update_profiles_in_database


class UserProfileBuilderTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()

    def test_update_all_user_profiles_in_database(self):
        user1 = struct.User.make_from_scratch(email='user1-test_update_user_profiles_in_database', interests=['interests1'])
        user2 = struct.User.make_from_scratch(email='user2-test_update_user_profiles_in_database', interests=['interests2'])
        self.dal.user.save_user(user1, 'password1')
        self.dal.user.save_user(user2, 'password2')
        feature_set_id = self._build_feature_set()
        doc = self._build_doc(feature_set_id)
        self.dal.doc.save_documents([doc])

        profile1 = self._build_profile(feature_set_id)
        self.dal.user_computed_profile.save_user_computed_profile(user1, profile1)

        self.dal.user_action.save_user_action_on_doc(
            user1, doc, struct.UserActionTypeOnDoc.up_vote)  # should be used because after save
        self.dal.user_action.save_user_action_on_doc(
            user2, doc, struct.UserActionTypeOnDoc.up_vote)  # should not be used

        profile2 = self._build_profile(feature_set_id)
        self.dal.user_computed_profile.save_user_computed_profile(user2, profile2)

        # identical action
        self.dal.user_action.save_user_action_on_doc(user1, doc, struct.UserActionTypeOnDoc.down_vote)
        self.dal.user_action.save_user_action_on_doc(user2, doc, struct.UserActionTypeOnDoc.down_vote)

        update_profiles_in_database()

        profiles = self.dal.user_computed_profile.get_user_computed_profiles([user1, user2])

        # user1 profile should prefer doc more thant user2
        self.assertGreater(profiles[0].feature_vector.vector[0], profiles[1].feature_vector.vector[0])

    def _build_feature_set(self):
        feature_set_id = 'test_update_user_profiles_in_database'
        self.dal.feature_set.save_feature_set(
            struct.FeatureSet.make_from_scratch(feature_set_id, ['feature_name'], None))
        return feature_set_id

    @staticmethod
    def _build_doc(feature_set_id):
        feature_vector = struct.FeatureVector.make_from_scratch([1.0], feature_set_id)
        doc = struct.Document.make_from_scratch('u1', 'h1', 't1', 's1', feature_vector)
        return doc

    @staticmethod
    def _build_profile(feature_set_id):
        feature_vector = struct.FeatureVector.make_from_scratch([1.0], feature_set_id)
        model_data = struct.UserProfileModelData.make_empty(1)
        return struct.UserComputedProfile.make_from_scratch(feature_vector, model_data)


if __name__ == '__main__':
    unittest.main()
