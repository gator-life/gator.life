# coding=utf-8
import os

import re
import unittest
import vcr
from scraper.scraper import _is_valid_link, _get_invalid_regex, _get_json_doc_generator
from common.scraperstructs import LinkElement

import jsonpickle
import jsonpickle.handlers
import jsonpickle.util

class ScraperTests(unittest.TestCase):

    def test_is_valid_link_match_regex_return_false(self):
        link = LinkElement("https://a.b.net/d-e/g.h/1_n.jpg?o=6", None, None, None)
        regex = re.compile('(1_n)')
        extensions = ['.inv']
        self.assertFalse(_is_valid_link(link, regex, extensions))

    def test_is_valid_link_filtered_extension_return_false(self):
        link = LinkElement("https://a.b.net/d-e/g.h/1_n.jpg?o=6", None, None, None)
        regex = re.compile('invalid')
        extensions = ['.inv', '.jpg']
        self.assertFalse(_is_valid_link(link, regex, extensions))

    def test_is_valid_link_good_url_return_true(self):
        link = LinkElement("https://a.b.net/d-e/g.h/1_n.jpg?o=6", None, None, None)
        regex = re.compile('invalid')
        extensions = ['.b', '.net']
        self.assertTrue(_is_valid_link(link, regex, extensions))

    def test_get_invalid_regex(self):
        regex = _get_invalid_regex()
        self.assertTrue(regex.search('vfgbvdfggyoutubedhkufjhc'))


    def test_get_json_doc_generator(self):
        jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=4, ensure_ascii=False)

        chinese = 'http://www.sina.com.cn/'
        jpg = 'https://scontent-dfw1-1.xx.fbcdn.net/hphotos-xat1/v/t1.0-9/11826008_10153591159909124_7497239512955988899_n.jpg?oh=026fe9cdf68e281f693c56f68f02a88b&oe=565454EE'  # pylint: disable=line-too-long
        pdf = 'http://www.math.stonybrook.edu/theses/thesis06-1/part1.pdf'
        russian = 'https://meduza.io/news/2015/08/01/v-administratsii-obamy-obsudili-vozmozhnost-vzloma-velikogo-kitayskogo-fayervola'  # pylint: disable=line-too-long
        english_and_russian = 'http://www.themoscowtimes.com/news/article/incompetence-and-corruption-taint-ukraines-military-performance/526447.html'  # pylint: disable=line-too-long
        french = 'http://lci.tf1.fr/france/faits-divers/meurthe-et-moselle-une-quarantaine-de-tombes-chretiennes-profanees-8641400.html'  # pylint: disable=line-too-long
        fail_decode = 'http://www.washingtonpost.com/news/worldviews/wp/2015/08/01/say-goodbye-to-the-weirdest-border-dispute-in-the-world/'  # pylint: disable=line-too-long
        fail_decode2 = 'http://nydn.us/1OFxpaN'
        fail_decode3 = 'http://happynicetimepeople.com/from-bloodsucking-cars-to-lava-spewing-spiders-syfy-makes-your-tv-dreams-come-true/'  # pylint: disable=line-too-long

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
        ]

        links = [LinkElement(url, None, None, None) for url in urls]

        directory = os.path.dirname(os.path.abspath(__file__))
        with vcr.use_cassette(directory + '/vcr_cassettes/test_get_json_doc_generator.yaml', record_mode='none'):
            json_docs = list(_get_json_doc_generator(links))

        decoded_docs = [jsonpickle.decode(d) for d in json_docs]

        self.assertEquals(5, len(json_docs))
        for doc in decoded_docs:
            html_content = doc.html_content
            self.assertIsInstance(html_content, unicode)

        self.assertTrue(u'Cimetière profané' in decoded_docs[0].html_content)
        self.assertTrue(u'которого власти Китая' in decoded_docs[1].html_content)
        self.assertTrue(u'Say goodbye to the weirdest' in decoded_docs[2].html_content)
        self.assertTrue(u'A former Florida church worker is accused' in decoded_docs[3].html_content)
        self.assertTrue(u'From bloodsucking cars to' in decoded_docs[4].html_content)

if __name__ == '__main__':
    unittest.main()





