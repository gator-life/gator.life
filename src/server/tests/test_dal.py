# coding=utf-8
import unittest
import itertools
from google.appengine.ext import ndb
from google.appengine.ext import testbed
import server.dal as dal
import server.dbentities as db


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
        db_doc1 = db.Document.make(url='url1', title='title1', summary=None)
        db_doc2 = db.Document.make(url='url2', title='title2', summary=None)

        feature1 = db.FeatureDescription.make('desc1')
        feature2 = db.FeatureDescription.make('desc2')
        feature_set = db.FeatureSet.make(feature_set_id='set', feature_descriptions=[feature1, feature2])
        ndb.put_multi([db_doc1, db_doc2, feature_set])  # we must store entities before creating user to init key fields

        doc1 = dal.Document(url=db_doc1.url, title=db_doc1.title, db_key=db_doc1.key)
        doc2 = dal.Document(url=db_doc2.url, title=db_doc2.title, db_key=db_doc2.key)

        feature_vector = dal.FeatureVector(vector=[0.5, 0.6], labels=['desc1', 'desc2'], feature_set_id=feature_set.key.id())

        user_docs = [dal.UserDocument(doc1, 0.1), dal.UserDocument(doc2, 0.2)]
        expected_user = dal.User(email='email', user_docs=user_docs, feature_vector=feature_vector)

        # ------------- Save then get user --------------
        dal.save_user(expected_user)
        result_user = dal.get_user('email')

        # --------------assert equality ------------------
        self.assertEquals(expected_user.email, result_user.email)

        expected_feat_vec = expected_user.feature_vector
        result_feat_vec = result_user.feature_vector
        self.assertEquals(expected_feat_vec.feature_set_id, result_feat_vec.feature_set_id)
        self.assertEquals(expected_feat_vec.vector, result_feat_vec.vector)
        self.assertEquals(expected_feat_vec.labels, result_feat_vec.labels)

        for (expected, result) in itertools.izip_longest(expected_user.user_docs, result_user.user_docs):
            self.assertEquals(expected.grade, result.grade)
            self.assertEquals(expected.document.title, result.document.title)


if __name__ == '__main__':
    unittest.main()
