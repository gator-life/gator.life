# coding=utf-8
import unittest
import itertools
import server.dal as sdal
import server.frontendstructs as struct
from common.datehelper import utcnow


class DalTests(unittest.TestCase):

    def setUp(self):
        self.dal = sdal.Dal()

    def test_save_then_get_features(self):
        self.dal.save_features(feature_set_id='set', feature_names=['desc1', 'desc2'])
        feature_set = self.dal.get_features('set')
        self.assertEquals('desc1', feature_set[0])
        self.assertEquals('desc2', feature_set[1])

    def test_save_then_get_empty_features(self):
        self.dal.save_features(feature_set_id='test_save_then_get_empty_features_feature_set_id', feature_names=[])
        feature_set = self.dal.get_features('test_save_then_get_empty_features_feature_set_id')
        self.assertEquals([], feature_set)

    def test_get_user_with_unknown_user_should_return_none(self):
        self.assertIsNone(self.dal.get_user('missing_user'))

    def test_save_then_get_user_should_be_equals(self):
        # ------ init database -----------
        password = 'password'
        expected_user = struct.User.make_from_scratch(email='email', interests=['interests'])

        # ------------- check save_user --------------
        self.assertIsNone(expected_user._user_computed_profile_db_key)
        self.assertIsNone(expected_user._user_doc_set_db_key)
        self.assertIsNone(expected_user._db_key)
        self.dal.save_user(expected_user, password)
        # save should init db keys
        self.assertIsNotNone(expected_user._user_doc_set_db_key)
        self.assertIsNotNone(expected_user._user_computed_profile_db_key)
        self.assertIsNotNone(expected_user._db_key)

        # ------------- check get_user --------------
        result_user = self.dal.get_user('email')
        self.assert_users_equals(expected_user, result_user)

        # ------- check get_user_and_password -------
        (result_user, result_password) = self.dal.get_user_and_password('email')
        self.assert_users_equals(expected_user, result_user)
        self.assertEquals(password, result_password)

    def assert_users_equals(self, expected_user, result_user):
        self.assertEquals(expected_user.email, result_user.email)
        self.assertEquals(expected_user.interests, result_user.interests)
        self.assertEquals(expected_user._user_doc_set_db_key, result_user._user_doc_set_db_key)
        self.assertEquals(expected_user._user_computed_profile_db_key, result_user._user_computed_profile_db_key)
        self.assertEquals(expected_user._db_key, result_user._db_key)

    def test_get_all_users(self):
        users_data = [('test_get_all_users_user1', ['interests1']),
                      ('test_get_all_users_user2', ['interests2']),
                      ('test_get_all_users_user3', ['interests3'])]
        for (email, interests) in users_data:
            self.dal.save_user(struct.User.make_from_scratch(email, interests), 'password')

        all_users = self.dal.get_all_users()
        all_users_this_test = [user for user in all_users if 'test_get_all_users' in user.email]

        self.assertEquals(3, len(all_users_this_test))

        result_users_data = sorted([(user.email, user.interests) for user in all_users_this_test],
                                   key=lambda user_data: user_data[0])
        for (expected, result) in zip(users_data, result_users_data):
            self.assertEquals(expected, result)

    def test_save_then_get_user_docs_should_be_equals(self):
        # setup : init docs in database
        doc1 = self.make_dummy_doc('test_save_then_get_user_docs_should_be_equals1')
        doc2 = self.make_dummy_doc('test_save_then_get_user_docs_should_be_equals2')
        self.dal.save_documents([doc1, doc2])

        expected_user_docs = [
            struct.UserDocument.make_from_scratch(doc1, 0.1),
            struct.UserDocument.make_from_scratch(doc2, 0.2)]

        # create user and save it to init user_document_set_key field
        user = struct.User.make_from_scratch("test_save_then_get_user_docs_should_be_equals", ["interests1"])
        self.dal.save_user(user, "password1")

        self.dal.save_user_docs(user, expected_user_docs)
        result_user_docs = self.dal.get_user_docs(user)
        self.assertEquals(len(expected_user_docs), len(result_user_docs))

        for (expected, result) in itertools.izip_longest(expected_user_docs, result_user_docs):
            self.assertEquals(expected.grade, result.grade)
            self.assertEquals(expected.document.title, result.document.title)

    def test_save_documents(self):
        feature_set_id = self.build_dummy_db_feature_set()
        feat_vec1 = struct.FeatureVector.make_from_scratch(vector=[0.5, 0.6], feature_set_id=feature_set_id)
        feat_vec2 = struct.FeatureVector.make_from_scratch(vector=[1.5, 0.6], feature_set_id=feature_set_id)

        expected_doc1 = struct.Document.make_from_scratch(
            url='url1_test_save_documents', title='title1_test_save_documents', summary='s1', feature_vector=feat_vec1)
        expected_doc2 = struct.Document.make_from_scratch(
            url='url2_test_save_documents', title='title2_test_save_documents', summary='s2', feature_vector=feat_vec2)
        expected_docs = [expected_doc1, expected_doc2]
        self.dal.save_documents(expected_docs)

        for expected_doc in expected_docs:
            result_doc = self.dal.get_doc_by_urlsafe_key(expected_doc.key_urlsafe)
            self.assertEquals(expected_doc.url, result_doc.url)
            self.assertEquals(expected_doc.title, result_doc.title)
            self.assertEquals(expected_doc.summary, result_doc.summary)
            self.assertEquals(expected_doc.feature_vector.vector[0], result_doc.feature_vector.vector[0])

    def test_save_then_get_computed_user_profiles(self):
        user1, profile1 = self._build_profile(1)
        user2, profile2 = self._build_profile(2)

        self.dal.save_computed_user_profiles([(user1, profile1), (user2, profile2)])
        result_profiles = self.dal.get_user_computed_profiles([user2, user1])
        self.assertEquals(2, len(result_profiles))
        self._assert_profiles_equals(profile1, result_profiles[1])
        self._assert_profiles_equals(profile2, result_profiles[0])

    def test_get_empty_computed_user_profile(self):
        user = struct.User.make_from_scratch(
            email='test_get_empty_computed_user_profiles', interests=[])
        self.dal.save_user(user, 'test_get_empty_computed_user_profiles_password')
        result_profile = self.dal.get_user_computed_profiles([user])[0]
        expected_profile = struct.UserComputedProfile.make_from_scratch(
            feature_vector=struct.FeatureVector.make_from_scratch([], sdal.NULL_FEATURE_SET),
            model_data=struct.UserProfileModelData.make_from_scratch([], [], [], 0, 0)
        )

        self._assert_profiles_equals(expected_profile, result_profile)

    def test_save_computed_user_profile(self):
        user, profile = self._build_profile(3)
        self.dal.save_computed_user_profile(user, profile)
        result_profile = self.dal.get_user_computed_profiles([user])[0]
        self._assert_profiles_equals(profile, result_profile)

    def test_get_users_feature_vectors(self):
        user1, profile1 = self._build_profile(4)
        user2, profile2 = self._build_profile(5)
        self.dal.save_computed_user_profiles([(user1, profile1), (user2, profile2)])

        vectors = self.dal.get_users_feature_vectors([user2, user1])

        self.assertEquals(2, len(vectors))
        self._assert_feature_vector_equals(profile1.feature_vector, vectors[1])
        self._assert_feature_vector_equals(profile2.feature_vector, vectors[0])

    def test_get_user_feature_vector(self):
        user, profile = self._build_profile(6)
        self.dal.save_computed_user_profiles([(user, profile)])
        vector = self.dal.get_user_feature_vector(user)
        self._assert_feature_vector_equals(profile.feature_vector, vector)

    def _build_profile(self, index):
        feature_set_id = self.build_dummy_db_feature_set()
        user = struct.User.make_from_scratch(email='user' + str(index), interests=['interests' + str(index)])
        self.dal.save_user(user, 'password' + str(index))
        feature_vector = struct.FeatureVector.make_from_scratch(
            vector=[0.5 + index, 0.6 + index], feature_set_id=feature_set_id)
        model_data = struct.UserProfileModelData.make_from_scratch(
            [0.7 + index, 0.8], [0.3 + index, 0.4], [-1.0 + index, -2.0], 5.0 + index, 9.0 + index)
        profile = struct.UserComputedProfile.make_from_scratch(feature_vector, model_data)
        return user, profile

    def _assert_profiles_equals(self, expected_profile, result_profile):
        self._assert_feature_vector_equals(expected_profile.feature_vector, result_profile.feature_vector)
        self._assert_model_data_equals(expected_profile.model_data, result_profile.model_data)

    def _assert_feature_vector_equals(self, expected_feature_vector, result_feature_vector):
        self.assertEquals(expected_feature_vector.vector, result_feature_vector.vector)
        self.assertEquals(expected_feature_vector.feature_set_id, result_feature_vector.feature_set_id)

    def _assert_model_data_equals(self, expected_model_data, result_model_data):
        self.assertEquals(expected_model_data.explicit_feedback_vector, result_model_data.explicit_feedback_vector)
        self.assertEquals(expected_model_data.positive_feedback_vector, result_model_data.positive_feedback_vector)
        self.assertEquals(expected_model_data.negative_feedback_vector, result_model_data.negative_feedback_vector)
        self.assertEquals(expected_model_data.positive_feedback_sum_coeff, result_model_data.positive_feedback_sum_coeff)
        self.assertEquals(expected_model_data.negative_feedback_sum_coeff, result_model_data.negative_feedback_sum_coeff)

    def test_save_then_get_users_docs_should_be_equals(self):

        doc1 = self.make_dummy_doc('test_save_then_get_users_docs_should_be_equals1')
        doc2 = self.make_dummy_doc('test_save_then_get_users_docs_should_be_equals2')
        self.dal.save_documents([doc1, doc2])

        # create user and save it to init user_document_set_key field
        user1 = struct.User.make_from_scratch("test_get_users_docs1", ["interests1"])
        user2 = struct.User.make_from_scratch("test_get_users_docs2", ["interests2"])
        self.dal.save_user(user1, "password1")
        self.dal.save_user(user2, "password2")

        expected_user1_docs = [
            struct.UserDocument.make_from_scratch(doc1, 0.1),
            struct.UserDocument.make_from_scratch(doc2, 0.2)]
        expected_user2_docs = [
            struct.UserDocument.make_from_scratch(doc1, 0.3)]

        self.dal.save_users_docs([(user1, expected_user1_docs), (user2, expected_user2_docs)])
        user_docs_by_user = self.dal.get_users_docs((user2, user1))

        self.assertEqual(2, len(user_docs_by_user))
        result_user2 = user_docs_by_user[0]
        result_user1 = user_docs_by_user[1]
        self.assertEqual(1, len(result_user2))
        self.assertEqual(2, len(result_user1))
        self.assertEqual(0.3, result_user2[0].grade)
        self.assertEqual(0.1, result_user1[0].grade)
        self.assertEqual(0.2, result_user1[1].grade)
        self.assertEqual(result_user1[0].document, result_user2[0].document)  # check that we use the same reference
        self.assertEqual(doc2.title, result_user1[1].document.title)

    def test_get_users_docs_zero_docs(self):
        user = struct.User.make_from_scratch("test_get_users_docs_zero_docs_user", ["interests1"])
        self.dal.save_user(user, "password")
        docs = self.dal.get_users_docs([user])[0]
        self.assertEquals([], docs)

    def test_get_user_no_interest(self):
        expected_user = struct.User.make_from_scratch("test_get_user_no_interest", [])
        self.dal.save_user(expected_user, "password")
        result_user = self.dal.get_user("test_get_user_no_interest")
        self.assert_users_equals(expected_user, result_user)

    def test_save_then_get_user_actions_on_doc(self):
        doc1 = self.make_dummy_doc('test_save_then_get_user_actions_on_doc1')
        doc2 = self.make_dummy_doc('test_save_then_get_user_actions_on_doc2')
        self.dal.save_documents([doc1, doc2])
        user1 = struct.User.make_from_scratch("test_save_then_get_user_actions_on_doc1", ["interests1"])
        user2 = struct.User.make_from_scratch("test_save_then_get_user_actions_on_doc2", ["interests2"])
        user3 = struct.User.make_from_scratch("test_save_then_get_user_actions_on_doc3", ["interests3"])
        self.dal.save_user(user1, "password1")
        self.dal.save_user(user2, "password2")
        self.dal.save_user(user3, "password3")
        self.dal.save_user_action_on_doc(user1, doc2, struct.UserActionTypeOnDoc.up_vote)  # before min_datetime, filtered

        min_datetime = utcnow()
        self.dal.save_user_action_on_doc(user1, doc1, struct.UserActionTypeOnDoc.up_vote)
        self.dal.save_user_action_on_doc(user2, doc1, struct.UserActionTypeOnDoc.down_vote)
        self.dal.save_user_action_on_doc(user1, doc2, struct.UserActionTypeOnDoc.click_link)
        self.dal.save_user_action_on_doc(user3, doc2, struct.UserActionTypeOnDoc.click_link)  # not in user list, filtered

        result = self.dal.get_user_actions_on_docs([user2, user1], min_datetime)

        self.assertEquals(2, len(result))
        user2_actions = result[0]
        user1_actions = result[1]
        self.assertEquals(1, len(user2_actions))
        user2_action = user2_actions[0]
        self.assertEquals(doc1.title, user2_action.document.title)
        self.assertEquals(struct.UserActionTypeOnDoc.down_vote, user2_action.action_type)
        self.assertTrue(min_datetime < user2_action.datetime)
        self.assertEquals(2, len(user1_actions))

    def make_dummy_doc(self, str_id):
        feature_set_id = self.build_dummy_db_feature_set()
        feat_vec = struct.FeatureVector.make_from_scratch(vector=[0.2], feature_set_id=feature_set_id)
        return struct.Document.make_from_scratch(
            url='url_' + str_id, title='title' + str_id, summary='s_' + str_id, feature_vector=feat_vec)

    # for each static member of the class (remove special fields __***__), check we do a proper round-trip with database
    def test_action_type_on_doc_mapping_with_db(self):
        for enum_name, enum_value in vars(struct.UserActionTypeOnDoc).iteritems():
            if not enum_name.startswith("__"):
                self.assertEquals(enum_value, sdal._to_user_action_type_on_doc(sdal._to_db_action_type_on_doc(enum_value)))

    def test_get_doc_by_urlsafe_key_exist(self):
        doc = self.make_dummy_doc('test_get_doc_by_urlsafe_key')
        self.dal.save_documents([doc])

        result_doc = self.dal.get_doc_by_urlsafe_key(doc.key_urlsafe)

        self.assertEquals(doc.url, result_doc.url)
        self.assertEquals(doc.title, result_doc.title)
        self.assertEquals(doc._db_key, result_doc._db_key)
        self.assertEquals(doc.key_urlsafe, result_doc.key_urlsafe)
        self.assertEquals(doc.summary, result_doc.summary)
        self.assertEquals(doc.feature_vector.vector, result_doc.feature_vector.vector)
        self.assertEquals(doc.feature_vector.feature_set_id, result_doc.feature_vector.feature_set_id)

    def build_dummy_db_feature_set(self):
        self.dal.save_features(feature_set_id='set', feature_names=['desc2', 'desc1'])
        return 'set'


if __name__ == '__main__':
    unittest.main()
