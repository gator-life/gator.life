# coding=utf-8

import re
import unittest
from scraper.scraper import _is_valid_link, _get_invalid_regex
from common.scraperstructs import LinkElement


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


if __name__ == '__main__':
    unittest.main()
