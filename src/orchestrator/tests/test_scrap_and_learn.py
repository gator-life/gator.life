#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from orchestrator.scrap_and_learn import _scrap_and_learn
from common.datehelper import utcnow
import scraper.scraperstructs as scrap
from server.dal import Dal
import server.frontendstructs as struct


class MockScraper(object):

    @staticmethod
    def scrap():
        def scrap_doc(index, content='html'):
            str_index = str(index)
            return scrap.Document(
                scrap.LinkElement(
                    "url" + str_index, None, scrap.OriginInfo("title" + str_index, None, None, None, None), None), content)

        # chunk_size(3) + 1
        # the before last document is an other instance of a duplicated url, should be ignored by the url unicity checker
        # the last document should ne ignored as it is returned as unclassifiable by the TopicModeller
        return [scrap_doc(3), scrap_doc(4), scrap_doc(5), scrap_doc(6), scrap_doc(3), scrap_doc(7, 'unclassifiable')]


class MockSaver(object):

    def __init__(self):
        self.saved_docs = []

    def save(self, doc):
        self.saved_docs.append(doc)


class MockTopicModeller(object):
    feature_vector = [1.0]

    @staticmethod
    def classify(doc_content):
        if doc_content == 'unclassifiable':
            return False, None
        if doc_content == 'html':
            return True, MockTopicModeller.feature_vector
        else:
            raise ValueError(doc_content)


class MockModelUpdater(object):

    def __init__(self, expected_topic_model, expected_users):
        self.expected_topic_model = expected_topic_model
        self.expected_users = expected_users
        self.updated = False

    def update_model_in_db(self, topic_modeller, all_users):
        if self.expected_topic_model != topic_modeller:
            raise ValueError(topic_modeller)
        if len(self.expected_users) != len(all_users):
            raise ValueError(all_users)
        self.updated = True


class ScrapAndLearnTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()
        self.ref_feature_set_id = 'feature_set_id_ScrapAndLearnTests'
        self.dal.feature_set.save_ref_feature_set_id(self.ref_feature_set_id)
        self.dummy_feat_vec = struct.FeatureVector.make_from_scratch([], self.ref_feature_set_id)

    def test_scrap_and_learn(self):
        # I)setup database and mocks
        # I.1) user
        user1 = struct.User.make_from_scratch("test_scrap_and_learn_user1", ["interests1"])
        self.dal.user.save_user(user1, "password1")
        self._save_dummy_profile_for_user(user1)
        user2 = struct.User.make_from_scratch("test_scrap_and_learn_user2", ["interests2"])
        self.dal.user.save_user(user2, "password2")
        self._save_dummy_profile_for_user(user2)
        # I.2) doc
        doc1 = struct.Document.make_from_scratch("url1", 'hash1', 'title1', "sum1", self.dummy_feat_vec)
        doc2 = struct.Document.make_from_scratch("url2", 'hash2', 'title2', "sum2", self.dummy_feat_vec)
        self.dal.doc.save_documents([doc1, doc2])
        # I.3) userDoc
        user1_user_docs = [
            struct.UserDocument.make_from_scratch(doc1, grade=0.0),  # this one should be removed
            struct.UserDocument.make_from_scratch(doc2, grade=1.0)]
        self.dal.user_doc.save_users_docs([(user1, user1_user_docs)])
        # II) Orchestrate
        topic_modeller = MockTopicModeller()
        mock_saver = MockSaver()
        model_updater = MockModelUpdater(topic_modeller, [user1, user2])
        _scrap_and_learn(MockScraper(), mock_saver, topic_modeller, model_updater, docs_chunk_size=2,
                         user_docs_max_size=5, seen_urls_cache_start_date=utcnow(),
                         keep_user_func=lambda u: 'test_scrap_and_learn' in u.email)

        # III) check database and mocks
        self.assertTrue(model_updater.updated)
        result_users_docs = self.dal.user_doc.get_users_docs([user1, user2])
        result_user1_docs = result_users_docs[0]
        result_user2_docs = result_users_docs[1]
        self.assertEquals(5, len(result_user1_docs))  # 5 because of user_docs_max_size=5
        self.assertEquals(4, len(result_user2_docs))
        for user_doc in result_user1_docs:
            if user_doc.document.title == 'title1':  # doc1 should have been deleted because grade=0.0
                self.fail()
        self.assertEquals(4, len(mock_saver.saved_docs))  # MockScraper generate 4 docs
        for doc in mock_saver.saved_docs:
            self.assertEquals(self.ref_feature_set_id, doc.feature_vector.feature_set_id)
            self.assertEquals(MockTopicModeller.feature_vector, doc.feature_vector.vector)

    def _save_dummy_profile_for_user(self, user):
        feature_vector = struct.FeatureVector.make_from_scratch([1.0], "featureSetId-test_scrap_learn")
        model_data = struct.UserProfileModelData.make_empty(1)
        self.dal.user_computed_profile.save_user_computed_profile(
            user, struct.UserComputedProfile.make_from_scratch(feature_vector, model_data))

if __name__ == '__main__':
    unittest.main()
