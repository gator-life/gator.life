#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from mock.mock import MagicMock
from scraper import reddit


class RedditTests(unittest.TestCase):

    def test_make_link_element(self):
        submission = MagicMock(url='my_url', title='my_title', subreddit=MagicMock(display_name='my_cat'),
                               permalink='orig_url', id='orig_id', subreddit_id='cat_id', created_utc=123456)

        link_elt = reddit._make_link_element(submission)

        self.assertEqual('my_url', link_elt.url)
        self.assertEqual('my_title', link_elt.origin_info.title)
        self.assertEqual('my_cat', link_elt.origin_info.category)
        self.assertEqual('orig_url', link_elt.origin_info.url)
        self.assertEqual('orig_id', link_elt.origin_info.unique_id)
        self.assertEqual('cat_id', link_elt.origin_info.category_id)
        self.assertEqual(123456, link_elt.date_utc_timestamp)
        self.assertEqual('reddit', link_elt.origin)

    def test_is_valid_submission_with_is_self_return_false(self):
        submission = MagicMock(is_self=True, over_18=False)
        self.assertFalse(reddit._is_valid_submission(submission))

    def test_is_valid_submission_with_over_18_return_false(self):
        submission = MagicMock(is_self=False, over_18=True)
        self.assertFalse(reddit._is_valid_submission(submission))

    def test_is_valid_submission_ok_return_false(self):
        submission = MagicMock(is_self=False, over_18=False)
        self.assertTrue(reddit._is_valid_submission(submission))

if __name__ == '__main__':
    unittest.main()
