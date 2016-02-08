# coding=utf-8

import unittest
from google.appengine.ext import ndb
from orchestrator.scrap_and_learn import scrap_and_learn
import scraper.scraperstructs as scrap
from common.testhelpers import make_gae_testbed
import server.dal as dal
import server.frontendstructs as struct


class MockScraper(object):

    @staticmethod
    def scrap():
        def scrap_doc(index):
            str_index = str(index)
            return scrap.Document(
                scrap.LinkElement(
                    "url" + str_index, None, scrap.OriginInfo("title" + str_index, None, None, None, None), None),
                'html')

        # chunk_size(3) + 1
        # the last document is an other instance of a duplicated url, should be ignored by the url unicity checker
        return [scrap_doc(3), scrap_doc(4), scrap_doc(5), scrap_doc(6), scrap_doc(3)]


class MockSaver(object):

    def __init__(self):
        self.saved_docs = []

    def save(self, doc):
        self.saved_docs.append(doc)


class MockTopicModeller(object):
    feature_vector = [1.0]

    @staticmethod
    def classify(doc_content):
        if doc_content == 'html':
            return MockTopicModeller.feature_vector
        else:
            raise ValueError(doc_content)


class MockUrlUnicityChecker(object):

    def __init__(self):
        self.urls_set = set()
        self.is_unique_count = 0
        self.saved_count = 0

    def is_unique(self, url):
        self.is_unique_count += 1

        prev_len = len(self.urls_set)

        self.urls_set.add(url)

        new_len = len(self.urls_set)

        return prev_len != new_len

    def save(self):
        self.saved_count += 1


class ScrapAndLearnTests(unittest.TestCase):

    def setUp(self):
        self.testbed = make_gae_testbed()
        ndb.get_context().clear_cache()
        self.dummy_feat_vec = struct.FeatureVector.make_from_scratch([], dal.NULL_FEATURE_SET)

    def tearDown(self):
        self.testbed.deactivate()  # pylint: disable=duplicate-code

    def test_scrap_and_learn(self):
        # I)setup database and mocks
        # I.1) user
        user1 = struct.User.make_from_scratch("user1")
        dal.save_user(user1)
        dal.save_user_feature_vector(user1, struct.FeatureVector.make_from_scratch([1.0], "featureSetId-test_orchestrate"))
        user2 = struct.User.make_from_scratch("user2")
        dal.save_user(user2)
        dal.save_user_feature_vector(user2, struct.FeatureVector.make_from_scratch([1.0], "featureSetId-test_orchestrate"))
        # I.2) doc
        doc1 = struct.Document.make_from_scratch("url1", 'title1', "sum1", self.dummy_feat_vec)
        doc2 = struct.Document.make_from_scratch("url2", 'title2', "sum2", self.dummy_feat_vec)
        dal.save_documents([doc1, doc2])
        # I.3) userDoc
        user1_user_docs = [
            struct.UserDocument.make_from_scratch(doc1, grade=0.0),  # this one should be removed
            struct.UserDocument.make_from_scratch(doc2, grade=1.0)]
        dal.save_users_docs([(user1, user1_user_docs)])
        # II) Orchestrate
        mock_saver = MockSaver()
        mock_url_unicity_checker = MockUrlUnicityChecker()
        scrap_and_learn(MockScraper(), mock_saver, MockTopicModeller(), mock_url_unicity_checker,
                        docs_chunk_size=2, user_docs_max_size=5)

        # III) check database and mocks
        result_users_docs = dal.get_users_docs([user1, user2])
        result_user1_docs = result_users_docs[0]
        result_user2_docs = result_users_docs[1]
        self.assertEquals(5, len(result_user1_docs))  # 5 because of user_docs_max_size=5
        self.assertEquals(4, len(result_user2_docs))
        for user_doc in result_user1_docs:
            if user_doc.document.title == 'title1':  # doc1 should have been deleted because grade=0.0
                self.fail()
        self.assertEquals(4, len(mock_saver.saved_docs))  # MockScraper generate 4 docs
        for doc in mock_saver.saved_docs:
            # currently, model versioning is not managed, all is set to ref
            self.assertEquals(dal.REF_FEATURE_SET, doc.feature_vector.feature_set_id)
            self.assertEquals(MockTopicModeller.feature_vector, doc.feature_vector.vector)
        # is_unique() should be called for each document
        self.assertEqual(mock_url_unicity_checker.is_unique_count, 5)
        # save() should be called at 'docs_chunk_size' frequency and 1 time at the end of the loop.
        self.assertEqual(mock_url_unicity_checker.saved_count, 3)


if __name__ == '__main__':
    unittest.main()
