# coding=utf-8

import logging
import os
import unittest
import vcr
import jsonpickle

from orchestrator.orchestrator import _to_json
from common.scraperstructs import Document, LinkElement
from scraper.scraper import _get_doc_generator

class OrchestratorTests(unittest.TestCase):

    def test_get_json_doc_generator(self):

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

        links = [LinkElement(url, None, None, None) for url in urls]

        with vcr.use_cassette(os.path.dirname(os.path.abspath(__file__)) + '/vcr_cassettes/test_get_doc_generator.yaml',
                              record_mode='none'):
            docs = list(_get_doc_generator(links))

        json_docs = [_to_json(d) for d in docs]
        decoded_docs = [jsonpickle.decode(d) for d in json_docs]

        self.assertEquals(5, len(json_docs))
        for doc in decoded_docs:
            self.assertIsInstance(doc, Document)
            html_content = doc.html_content
            self.assertIsInstance(html_content, unicode)

        self.assertTrue(u'Cimetière profané' in decoded_docs[0].html_content)
        self.assertTrue(u'которого власти Китая' in decoded_docs[1].html_content)
        self.assertTrue(u'Say goodbye to the weirdest' in decoded_docs[2].html_content)
        self.assertTrue(u'A former Florida church worker is accused' in decoded_docs[3].html_content)
        self.assertTrue(u'From bloodsucking cars to' in decoded_docs[4].html_content)


if __name__ == '__main__':
    unittest.main()
