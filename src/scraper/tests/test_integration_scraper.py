#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import vcr

from scraper.scraper import Scraper


class ScraperIntegrationTests(unittest.TestCase):

    # to record:
    #   set disconnected=False (to set 2sec delay between requests)
    #   delete test_run_scraper.yaml
    #   set record_mode='once'
    def test_scrap(self):
        nb_doc = 4  # to keep test short
        curr_doc = 0
        scraper = Scraper(disconnected=True)
        directory = os.path.dirname(os.path.abspath(__file__))
        with vcr.use_cassette(directory + '/vcr_cassettes/test_run_scraper.yaml', record_mode='none', ignore_localhost=True):
            for doc in scraper.scrap():
                self.assertIsInstance(doc.url, unicode)
                self.assertIsInstance(doc.title, unicode)
                self.assertIsInstance(doc.content, unicode)
                self.assertNotIn(u'.gif', doc.url)  # check extension filter
                self.assertNotIn(u'youtu', doc.url)  # check regex filter

                curr_doc += 1
                if curr_doc == nb_doc:
                    break
            else:
                self.fail('error: not enough docs extracted from cassette, should be '
                          + str(nb_doc) + ', was ' + str(curr_doc))

if __name__ == '__main__':
    unittest.main()
