# -*- coding: utf-8 -*-

import os
import unittest
from common.UrlUnicityChecker import UrlUnicityChecker


class UrlUnicityCheckerTests(unittest.TestCase):

    def setUp(self):
        self.serialized_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'serialized.bin')

    def tearDown(self):
        os.remove(self.serialized_path)

    def test_url_unicity_checker(self):
        url_unicity_checker = UrlUnicityChecker(self.serialized_path)

        self.assertEqual(len(url_unicity_checker.hashed_urls_set), 0)

        url1 = 'url1'
        url2 = 'url2'

        self.assertTrue(url_unicity_checker.is_unique(url1))
        self.assertTrue(url_unicity_checker.is_unique(url2))
        self.assertEqual(len(url_unicity_checker.hashed_urls_set), 2)
        self.assertFalse(url_unicity_checker.is_unique(url1))
        self.assertEqual(len(url_unicity_checker.hashed_urls_set), 2)

        url_unicity_checker.save()

        new_url_unicity_checker = UrlUnicityChecker(self.serialized_path)

        self.assertFalse(new_url_unicity_checker.is_unique(url2))
        self.assertEqual(len(new_url_unicity_checker.hashed_urls_set), 2)

        url3 = 'url3'

        self.assertTrue(new_url_unicity_checker.is_unique(url3))
        self.assertEqual(len(new_url_unicity_checker.hashed_urls_set), 3)


if __name__ == '__main__':
    unittest.main()
