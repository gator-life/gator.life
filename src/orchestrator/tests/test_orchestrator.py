# coding=utf-8

import logging
import os
import unittest
import vcr
import jsonpickle

from orchestrator.orchestrator import _setup_env, _orchestrate
import scraper.scraperstructs as scrap
from scraper.scraper import _get_doc_generator
from google.appengine.ext import ndb
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

        return [scrap_doc(3), scrap_doc(4), scrap_doc(5), scrap_doc(6)] # chunk_size(3) + 1

class MockSaver(object):
    def __init__(self):
        self.saved_docs = []

    def save(self, doc):
        self.saved_docs.append(doc)


class MockTopicModeller(object):
    @staticmethod
    def classify(doc_content):
        if doc_content == 'html':
            return [1.0]
        else:
            raise ValueError(doc_content)


class OrchestratorTests(unittest.TestCase):

    def setUp(self):
        self.testbed = make_gae_testbed()
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()  # pylint: disable=duplicate-code

    def test_orchestrate(self):
        # I)setup database and mocks
        # I.1) user
        user1 = struct.User.make_from_scratch("user1")
        dal.save_user(user1)
        dal.save_user_feature_vector(user1, struct.FeatureVector.make_from_scratch([1.0], "featureSetId-test_orchestrate"))
        user2 = struct.User.make_from_scratch("user2")
        dal.save_user(user2)
        dal.save_user_feature_vector(user2, struct.FeatureVector.make_from_scratch([1.0], "featureSetId-test_orchestrate"))
        # I.2) doc
        doc1 = struct.Document.make_from_scratch("url1", 'title1', "sum1")
        doc2 = struct.Document.make_from_scratch("url2", 'title2', "sum2")
        dal.save_documents([doc1, doc2])
        # I.3) userDoc
        dal.save_users_docs([(user1, [struct.UserDocument.make_from_scratch(doc1, grade=0.0)])])  # should be removed
        dal.save_users_docs([(user1, [struct.UserDocument.make_from_scratch(doc2, grade=1.0)])])
        # II) Orchestrate
        mock_saver = MockSaver()
        _orchestrate(MockScraper(), mock_saver, MockTopicModeller(), docs_chunk_size=3, user_docs_max_size=5)

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

    # todo: Move back this test into scraper (and associated cassette)
    def test_get_json_doc_generator(self):
        _setup_env()

        logging.disable('WARNING')  # this test raise logged exceptions, we disable it to not pollute console output

        chinese = 'http://www.sina.com.cn/'
        jpg = 'https://scontent-dfw1-1.xx.fbcdn.net/hphotos-xat1/v/t1.0-9/11826008_10153591159909124_7497239512955988899_n.jpg?oh=026fe9cdf68e281f693c56f68f02a88b&oe=565454EE'  # pylint: disable=line-too-long
        pdf = 'http://www.math.stonybrook.edu/theses/thesis06-1/part1.pdf'
        russian = 'https://meduza.io/news/2015/08/01/v-administratsii-obamy-obsudili-vozmozhnost-vzloma-velikogo-kitayskogo-fayervola'  # pylint: disable=line-too-long
        english_and_russian = 'http://www.themoscowtimes.com/news/article/incompetence-and-corruption-taint-ukraines-military-performance/526447.html'  # pylint: disable=line-too-long
        french = 'http://lci.tf1.fr/france/faits-divers/meurthe-et-moselle-une-quarantaine-de-tombes-chretiennes-profanees-8641400.html'  # pylint: disable=line-too-long
        fail_decode = 'http://www.washingtonpost.com/news/worldviews/wp/2015/08/01/say-goodbye-to-the-weirdest-border-dispute-in-the-world/'  # pylint: disable=line-too-long
        fail_decode2 = 'http://nydn.us/1OFxpaN'
        fail_decode3 = 'http://happynicetimepeople.com/from-bloodsucking-cars-to-lava-spewing-spiders-syfy-makes-your-tv-dreams-come-true/'  # pylint: disable=line-too-long
        unicode_decode_error_exception = 'http://www.dezeen.com/2015/08/05/charles-holland-lost-relics-postmodernism-architecture-design/'  # pylint: disable=line-too-long

        urls = [
            french,  # ok
            russian,  # ok
            chinese,  # filtered
            jpg,  # filtered
            pdf,  # filtered
            english_and_russian,  # filtered
            fail_decode,  # ok
            fail_decode2,  # ok
            fail_decode3,  # ok
            unicode_decode_error_exception,  # filtered
        ]

        links = [scrap.LinkElement(url, None, None, None) for url in urls]

        with vcr.use_cassette(os.path.dirname(os.path.abspath(__file__)) + '/vcr_cassettes/test_get_doc_generator.yaml',
                              record_mode='none'):
            docs = list(_get_doc_generator(links))

        json_docs = [jsonpickle.encode(d) for d in docs]
        decoded_docs = [jsonpickle.decode(d) for d in json_docs]

        self.assertEquals(5, len(json_docs))
        for doc in decoded_docs:
            self.assertIsInstance(doc, scrap.Document)
            html_content = doc.html_content
            self.assertIsInstance(html_content, unicode)

        self.assertTrue(u'Cimetière profané' in decoded_docs[0].html_content)
        self.assertTrue(u'которого власти Китая' in decoded_docs[1].html_content)
        self.assertTrue(u'Say goodbye to the weirdest' in decoded_docs[2].html_content)
        self.assertTrue(u'A former Florida church worker is accused' in decoded_docs[3].html_content)
        self.assertTrue(u'From bloodsucking cars to' in decoded_docs[4].html_content)


if __name__ == '__main__':
    unittest.main()
