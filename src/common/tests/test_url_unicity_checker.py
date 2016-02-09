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

        url1 = 'url1'
        url2 = 'url2'

        self.assertTrue(url_unicity_checker.is_unique_and_add(url1))
        self.assertTrue(url_unicity_checker.is_unique_and_add(url2))
        self.assertFalse(url_unicity_checker.is_unique_and_add(url1))

        url_unicity_checker.save()

        new_url_unicity_checker = UrlUnicityChecker(self.serialized_path)

        self.assertFalse(new_url_unicity_checker.is_unique_and_add(url2))

        url3 = 'url3'

        self.assertTrue(new_url_unicity_checker.is_unique_and_add(url3))


if __name__ == '__main__':
    unittest.main()
