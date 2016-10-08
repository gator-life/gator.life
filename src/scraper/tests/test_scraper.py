#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
import unittest
import os
from collections import namedtuple
import vcr
import jsonpickle
from scraper.scraper import _is_valid_link, _get_invalid_regex, _get_doc_generator, _HtmlExtractor
from scraper.scraperstructs import LinkElement, Document


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

    def test_html_extractor_try_get_html_with_long_html_return_none(self):

        def get_valid_html_utf8_str(str_size):
            # the 'é' char is a special character and count for 2 char when doing len(string). We don't want to do
            # complex decoding just for this rough size check so we let it count for 2
            # ie: we let é*499000 to pass and é*500000 to fail
            utf8_size = str_size / 2
            long_string = u"é" * utf8_size  # more than 1M char, 'é' to force guessed_encoding to utf-8 (else it gives ASCII)
            html_doc = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>title</title>
      </head>
      <body>
        <!""" + long_string.encode('utf-8') + """/>
      </body>
    </html>
    """
            return html_doc

        ok_html_doc = get_valid_html_utf8_str(999000)  # take 1k margin because there is the html around
        too_long_html_doc = get_valid_html_utf8_str(1000000)
        ok_doc_url = 'ok_url'
        too_long_doc_url = 'ko_url'

        # mock of requests lib
        class RequestsLongDocMock(object):

            # mock requests.get
            def get(self, url, timeout):  # pylint: disable=unused-argument, no-self-use
                # return a mock result result with same fields as result type from requests.get(url)
                html_doc = ok_html_doc if url == ok_doc_url else too_long_html_doc
                request_result = namedtuple('request_data', ['encoding', 'content', 'text'])
                return request_result(encoding='utf-8', content=html_doc, text=html_doc)

        html_extractor = _HtmlExtractor()
        html_extractor._requests = RequestsLongDocMock()  # set mock requests lib
        # the 2 calls with only the size differing are here to ensure that is the reason too_long_doc_url fails
        self.assertIsNotNone(html_extractor.try_get_html(ok_doc_url))
        self.assertIsNone(html_extractor.try_get_html(too_long_doc_url))

    def test_get_doc_generator_return_docs_correctly_serializable_as_json(self):
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
                              record_mode='none', ignore_localhost=True):
            docs = list(_get_doc_generator(links))

        json_docs = [jsonpickle.encode(d) for d in docs]
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
