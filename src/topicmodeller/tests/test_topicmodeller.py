#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topicmodeller.topicmodeller import TopicModeller, _decode, _filter_latin_words, _readable_document, \
    _remove_stop_words, _word_tokenize

import os
import unittest


class TopicModellerTests(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir('tm_data'):
            os.makedirs('tm_data')
        for tm_file in os.listdir('tm_data'):
            os.remove(os.path.join('tm_data', tm_file))

    def test_readable_document(self):
        directory = os.path.dirname(os.path.abspath(__file__))
        html_content = _decode(open(os.path.join(directory, 'scraper_documents/2015-08-01 18:00:22.926317_8.json'))
                               .read()).html_content
        readable_document = _readable_document(html_content)

        self.assertTrue(u'just aired its thrilling, flame thrower-filled, metal shrapnel-rich'
                        in readable_document)
        self.assertTrue(u'1.) Continue to emphasize the competition as a sport.'
                        in readable_document)

    def test_word_tokenize(self):
        document = u"\"BattleBots\" producers are definitely looking forward and feeling confident that ABC will renew " \
                   u"the series for a second season (seventh if you count the five seasons it ran on Comedy Central from " \
                   u"2000 to 2002). And they've definitely given some thought as to what they'd like to do similarly and " \
                   u"what they'd like to change up."
        word_tokenized = _word_tokenize(document)

        words = [u'will', u'renew', u'the', u'series', u'for', u'a', u'second', u'season', u'seventh', u'if', u'you',
                 u'count']
        self.assertTrue(all(x in word_tokenized for x in words))

    def test_remove_stop_words(self):
        document = [u'``', u'BattleBots', u"''", u'producers', u'are', u'definitely', u'looking', u'forward', u'and',
                    u'feeling', u'confident', u'that', u'ABC', u'will', u'renew', u'the', u'series', u'for', u'a', u'second',
                    u'season', u'(', u'seventh', u'if', u'you', u'count', u'the', u'five', u'seasons', u'it', u'ran', u'on',
                    u'Comedy', u'Central', u'from', u'2000', u'to', u'2002', u')', u'.', u'And', u'they', u"'ve",
                    u'definitely', u'given', u'some', u'thought', u'as', u'to', u'what', u'they', u"'d", u'like', u'to',
                    u'do', u'similarly', u'and', u'what', u'they', u"'d", u'like', u'to', u'change', u'up', u'.']

        stop_words_removed = _remove_stop_words(document)

        words = [u'this', u'that', u'at', u'the', u'a', u'is', u'are', u'was']
        self.assertTrue(all(x not in stop_words_removed for x in words))

    def test_filter_latin_words(self):
        words = [u'I', u'know', u'how', u'to', u'do', u'it']
        self.assertTrue(words == _filter_latin_words(words))

        self.assertTrue(not _filter_latin_words([u'1000']))

    def test_initialize_tm_dictionary(self):
        tm_documents = [[[u'BattleBots', u'producers', u'definitely', u'looking', u'forward', u'feeling', u'confident',
                          u'ABC', u'renew', u'series', u'second', u'season', u'seventh', u'count', u'five', u'seasons',
                          u'ran', u'Comedy', u'Central', u'And', u'\'ve', u'definitely', u'given', u'thought', u'like',
                          u'similarly', u'like', u'change'],
                         [u'In', u'many', u'ways', u'an', u'open', u'ournament', u'helps', u'here', u'But', u'the',
                          u'producers', u'encourage', u'competitors', u'to', u'find', u'loopholes', u'in', u'the',
                          u'rules']]]

        topicmodeller = TopicModeller()
        topicmodeller.initialize(tm_documents, num_topics=2)

        all_words = (word for batched_document in tm_documents
                     for document in batched_document
                     for word in document)

        self.assertTrue(all(word in topicmodeller.dictionary.values() for word in all_words))


if __name__ == '__main__':
    unittest.main()
