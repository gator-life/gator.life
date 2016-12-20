#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
import unittest
import os
from collections import namedtuple
import vcr
from scraper.scraper import Document, _is_valid_link, _get_invalid_regex, _get_doc_generator, _HtmlExtractor,\
    _try_get_document
from scraper.reddit import LinkElement


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
            @staticmethod
            def get(url, timeout):  # pylint: disable=unused-argument
                # return a mock result result with same fields as result type from requests.get(url)
                html_doc = ok_html_doc if url == ok_doc_url else too_long_html_doc
                request_result = namedtuple('request_result', ['encoding', 'content', 'text'])
                return request_result(encoding='utf-8', content=html_doc, text=html_doc)

            @staticmethod
            def head(url, timeout):  # pylint: disable=unused-argument
                request_head = namedtuple('request_head', ['headers'])
                return request_head(headers={"Content-Type": "text/html"})

        html_extractor = _HtmlExtractor()
        html_extractor._requests = RequestsLongDocMock()  # set mock requests lib
        # the 2 calls with only the size differing are here to ensure that is the reason too_long_doc_url fails
        self.assertIsNotNone(html_extractor.try_get_html(ok_doc_url))
        self.assertIsNone(html_extractor.try_get_html(too_long_doc_url))

    def test_get_doc_generator_return_docs_correctly_serializable_as_json(self):
        logging.disable('WARNING')  # this test raise logged exceptions, we disable it to not pollute console output

        chinese = u'http://www.sina.com.cn/'
        jpg = u'https://scontent-dfw1-1.xx.fbcdn.net/hphotos-xat1/v/t1.0-9/11826008_10153591159909124_7497239512955988899_n.jpg?oh=026fe9cdf68e281f693c56f68f02a88b&oe=565454EE'  # pylint: disable=line-too-long
        pdf = u'http://www.math.stonybrook.edu/theses/thesis06-1/part1.pdf'
        russian = u'https://meduza.io/news/2015/08/01/v-administratsii-obamy-obsudili-vozmozhnost-vzloma-velikogo-kitayskogo-fayervola'  # pylint: disable=line-too-long
        french = u'http://www.liberation.fr/france/2016/12/06/a-new-york-macron-trace-sa-route-a-l-americaine_1533374'
        fail_decode = u'http://www.washingtonpost.com/news/worldviews/wp/2015/08/01/say-goodbye-to-the-weirdest-border-dispute-in-the-world/'  # pylint: disable=line-too-long
        fail_decode2 = u'http://happynicetimepeople.com/from-bloodsucking-cars-to-lava-spewing-spiders-syfy-makes-your-tv-dreams-come-true/'  # pylint: disable=line-too-long
        unicode_decode_error_exception = u'http://www.dezeen.com/2015/08/05/charles-holland-lost-relics-postmodernism-architecture-design/'  # pylint: disable=line-too-long

        urls = [
            french,  # ok
            russian,  # ok
            chinese,  # filtered
            jpg,  # filtered
            pdf,  # filtered
            fail_decode,  # ok
            fail_decode2,  # ok
            unicode_decode_error_exception,  # filtered
        ]

        links = [LinkElement(url, None, None, None) for url in urls]

        with vcr.use_cassette(os.path.dirname(os.path.abspath(__file__)) + '/vcr_cassettes/test_get_doc_generator.yaml',
                              record_mode='none', ignore_localhost=True):
            docs = list(_get_doc_generator(links))

        self.assertEquals(4, len(docs))
        for doc in docs:
            self.assertIsInstance(doc, Document)
            self.assertIsInstance(doc.content, unicode)
            self.assertIsInstance(doc.title, unicode)
            self.assertTrue(doc.url in urls)

        self.assertTrue(u'secrétaire général des Nations-Unies, António Guterres' in docs[0].content)
        self.assertTrue(u'которого власти Китая' in docs[1].content)
        self.assertTrue(u'but on the ground it is likely to be far more complicated' in docs[2].content)
        self.assertTrue(u'I could just simply throw you an actual arm and a leg' in docs[3].content)

    def test_try_get_document_valid_input(self):
        html_doc = u"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>this is title</title>
      </head>
      <body>this is content</body>
    </html>
    """

        url = u'url_test_try_get_document_valid_input'
        scraper_doc = _try_get_document(url, html_doc)
        self.assertEquals(url, scraper_doc.url)
        self.assertEquals(u'this is title', scraper_doc.title)
        self.assertEquals(u'this is content', scraper_doc.content)

    def test_try_get_document_no_title_return_none(self):
        html_doc = u"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title></title>
      </head>
      <body>
        this is content
      </body>
    </html>
    """

        url = u'url_test_try_get_document_valid_input'
        self.assertIsNone(_try_get_document(url, html_doc))

    def test_try_get_document_no_content_return_none(self):
        html_doc = u"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>this is title</title>
      </head>
      <body></body>
    </html>
    """

        url = u'url_test_try_get_document_valid_input'
        self.assertIsNone(_try_get_document(url, html_doc))

if __name__ == '__main__':
    unittest.main()
