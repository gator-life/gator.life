#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from server.structinit import create_user_in_db
from server.dal import Dal, REF_FEATURE_SET
import server.passwordhelpers as pswd


class StructInitTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()
        self.dal.feature_set.save_features(REF_FEATURE_SET, feature_names=['f1', 'f2', 'f3', 'f4'])

    def test_create_user_in_db(self):
        email = 'email_test_create_user_in_db'
        interests = ['test_create_user_in_db_interest1', 'test_create_user_in_db_interest2']
        password = 'password_test_create_user_in_db'
        user = create_user_in_db(email, interests, password, self.dal)

        user_from_db, hash_password_from_db = self.dal.user.get_user_and_password(email)
        profile = self.dal.user_computed_profile.get_user_computed_profiles([user])[0]

        self.assertEquals(email, user.email)
        self.assertEquals(email, user_from_db.email)
        self.assertEquals(interests, user.interests)
        self.assertEquals(interests, user_from_db.interests)
        self.assertEquals(pswd.hash_password(password), hash_password_from_db)
        self.assertEquals(REF_FEATURE_SET, profile.feature_vector.feature_set_id)
        self.assertEquals([1, 1, 1, 1], profile.feature_vector.vector)
        self.assertEquals(4, len(profile.model_data.positive_feedback_vector))


if __name__ == '__main__':
    unittest.main()
