# coding=utf-8
import unittest
import itertools
from google.appengine.ext import ndb
from google.appengine.ext import testbed
import server.dal as dal
import server.dbentities as db
import server.frontendstructs as struct


class DalTests(unittest.TestCase):
    def setUp(self):
        # standard set of calls to initialize unit test ndb environment
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    def test_get_features(self):
        feature1 = db.FeatureDescription.make('desc1')
        feature2 = db.FeatureDescription.make('desc2')
        db.FeatureSet.make(feature_set_id='set', feature_descriptions=[feature1, feature2]).put()
        feature_set = dal.get_features('set')
        self.assertEquals('desc1', feature_set[0])
        self.assertEquals('desc2', feature_set[1])

    def test_get_user_with_unknown_user_should_return_none(self):
        self.assertIsNone(dal.get_user('missing_user'))

    def test_save_then_get_user_should_be_equals(self):
        # ------ init database -----------
        user_email = 'email'
        expected_user = struct.User.make_from_scratch(email=user_email)

        # ------------- check save_user --------------
        self.assertIsNone(expected_user._feature_vector_db_key)
        self.assertIsNone(expected_user._user_doc_set_db_key)
        dal.save_user(expected_user)
        # save should init db keys
        self.assertIsNotNone(expected_user._user_doc_set_db_key)
        self.assertIsNotNone(expected_user._feature_vector_db_key)

        # ------------- check get_user --------------
        result_user = dal.get_user('email')
        self.assertEquals(expected_user.email, result_user.email)
        self.assertEquals(expected_user._user_doc_set_db_key, result_user._user_doc_set_db_key)
        self.assertEquals(expected_user._feature_vector_db_key, result_user._feature_vector_db_key)

    def test_get_all_users(self):
        users_email = ['user1', 'user2', 'user3']
        for email in users_email:
            dal.save_user(struct.User.make_from_scratch(email=email))

        all_users = dal.get_all_users()
        self.assertEquals(3, len(all_users))

        result_user_emails = sorted([user.email for user in all_users])
        for (expected, result) in zip(users_email, result_user_emails):
            self.assertEquals(expected, result)

    def test_save_then_get_user_docs_should_be_equals(self):
        # setup : init docs in database
        db_doc1 = db.Document.make(url='url1', title='title1', summary=None)
        db_doc2 = db.Document.make(url='url2', title='title2', summary=None)
        ndb.put_multi([db_doc1, db_doc2])

        doc1 = struct.Document.make_from_db(
            url=db_doc1.url, title=db_doc1.title, summary=None, date=None, db_key=db_doc1.key)
        doc2 = struct.Document.make_from_db(
            url=db_doc2.url, title=db_doc2.title, summary=None, date=None, db_key=db_doc2.key)

        expected_user_docs = [
            struct.UserDocument.make_from_scratch(doc1, 0.1),
            struct.UserDocument.make_from_scratch(doc2, 0.2)]

        # create user and save it to init user_document_set_key field
        user = struct.User.make_from_scratch("test_save_then_get_user_docs_should_be_equals")
        dal.save_user(user)

        dal.save_user_docs(user, expected_user_docs)
        result_user_docs = dal.get_user_docs(user)
        self.assertEquals(len(expected_user_docs), len(result_user_docs))

        for (expected, result) in itertools.izip_longest(expected_user_docs, result_user_docs):
            self.assertEquals(expected.grade, result.grade)
            self.assertEquals(expected.document.title, result.document.title)

    def test_save_documents(self):
        expected_doc1 = struct.Document.make_from_scratch(
            url='url1_test_save_documents', title='title1_test_save_documents', summary='summary1')
        expected_doc2 = struct.Document.make_from_scratch(
            url='url2_test_save_documents', title='title1_test_save_documents', summary='summary2')
        expected_docs = [expected_doc1, expected_doc2]
        dal.save_documents(expected_docs)

        for expected_doc in expected_docs:
            result_doc = expected_doc._db_key.get()
            self.assertEquals(expected_doc.url, result_doc.url)
            self.assertEquals(expected_doc.title, result_doc.title)
            self.assertEquals(expected_doc.summary, result_doc.summary)

    def test_save_then_get_user_feature_vector_should_be_equals(self):
        feature_set = self.build_dummy_feature_set()
        expected_feat_vec = struct.FeatureVector.make_from_scratch(
            vector=[0.5, 0.6], feature_set_id=feature_set.key.id())

        user = struct.User.make_from_scratch('test_save_then_get_user_feature_vector_should_be_equals')
        dal.save_user(user)
        dal.save_user_feature_vector(user, expected_feat_vec)

        result_feat_vec = dal.get_user_feature_vector(
            dal.get_user('test_save_then_get_user_feature_vector_should_be_equals')
        )
        self.assertEquals(expected_feat_vec.feature_set_id, result_feat_vec.feature_set_id)
        self.assertEquals(expected_feat_vec.vector, result_feat_vec.vector)

    def test_get_users_feature_vectors(self):
        user1 = struct.User.make_from_scratch('test_get_users_feature_vectors1')
        user2 = struct.User.make_from_scratch('test_get_users_feature_vectors2')
        dal.save_user(user1)
        dal.save_user(user2)
        feature_set = self.build_dummy_feature_set()
        feat_vec_1 = struct.FeatureVector.make_from_scratch(
            vector=[0.2], feature_set_id=feature_set.key.id())
        feat_vec_2 = struct.FeatureVector.make_from_scratch(
            vector=[0.1], feature_set_id=feature_set.key.id())
        dal.save_user_feature_vector(user1, feat_vec_1)
        dal.save_user_feature_vector(user2, feat_vec_2)
        result_vectors = dal.get_users_feature_vectors([user2, user1])
        self.assertEqual(0.1, result_vectors[0].vector[0])
        self.assertEqual(0.2, result_vectors[1].vector[0])

    def test_save_then_get_users_docs_should_be_equals(self):

        doc1 = struct.Document.make_from_scratch(url='url1', title='title1', summary='')
        doc2 = struct.Document.make_from_scratch(url='url2', title='title2', summary='')
        dal.save_documents([doc1, doc2])

        # create user and save it to init user_document_set_key field
        user1 = struct.User.make_from_scratch("test_get_users_docs1")
        user2 = struct.User.make_from_scratch("test_get_users_docs2")
        dal.save_user(user1)
        dal.save_user(user2)

        expected_user1_docs = [
            struct.UserDocument.make_from_scratch(doc1, 0.1),
            struct.UserDocument.make_from_scratch(doc2, 0.2)]
        expected_user2_docs = [
            struct.UserDocument.make_from_scratch(doc1, 0.3)]

        dal.save_users_docs({user1: expected_user1_docs, user2: expected_user2_docs})
        user_docs_by_user = dal.get_users_docs((user2, user1))

        self.assertEqual(2, len(user_docs_by_user))
        result_user2 = user_docs_by_user[0]
        result_user1 = user_docs_by_user[1]
        self.assertEqual(1, len(result_user2))
        self.assertEqual(2, len(result_user1))
        self.assertEqual(0.3, result_user2[0].grade)
        self.assertEqual(0.1, result_user1[0].grade)
        self.assertEqual(0.2, result_user1[1].grade)
        self.assertEqual(result_user1[0].document, result_user2[0].document)  # check that we use the same reference
        self.assertEqual('title2', result_user1[1].document.title)

    @staticmethod
    def build_dummy_feature_set():
        feature2 = db.FeatureDescription.make('desc2')
        feature1 = db.FeatureDescription.make('desc1')
        feature_set = db.FeatureSet.make(feature_set_id='set', feature_descriptions=[feature1, feature2])
        feature_set.put()
        return feature_set


if __name__ == '__main__':
    unittest.main()
