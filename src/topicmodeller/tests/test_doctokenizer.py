#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
import jsonpickle
from topicmodeller.doctokenizer import _filter_latin_words, _readable_document, _remove_stop_words, _word_tokenize, \
    DocTokenizerFromHtml, DocTokenizerFromRawText


class DocTokenizerTests(unittest.TestCase):

    def test_readable_document(self):
        directory = os.path.dirname(os.path.abspath(__file__))
        file_content = open(os.path.join(directory, 'scraper_documents/2015-08-01 18:00:22.926317_8.json')).read()
        html_content = jsonpickle.decode(file_content).html_content
        readable_document = _readable_document(html_content)

        self.assertTrue('just aired its thrilling, flame thrower-filled, metal shrapnel-rich'
                        in readable_document)
        self.assertTrue('1.) Continue to emphasize the competition as a sport.'
                        in readable_document)

    def test_word_tokenize(self):
        document = "\"BattleBots\" producers are definitely looking forward and feeling confident that ABC will renew " \
                   "the series for a second season (seventh if you count the five seasons it ran on Comedy Central from " \
                   "2000 to 2002). And they've definitely given some thought as to what they'd like to do similarly and " \
                   "what they'd like to change up."
        word_tokenized = _word_tokenize(document)

        words = ['will', 'renew', 'the', 'series', 'for', 'a', 'second', 'season', 'seventh', 'if', 'you',
                 'count']
        self.assertTrue(all(x in word_tokenized for x in words))

    def test_remove_stop_words(self):
        document = ['``', 'BattleBots', "''", 'producers', 'are', 'definitely', 'looking', 'forward', 'and',
                    'feeling', 'confident', 'that', 'ABC', 'will', 'renew', 'the', 'series', 'for', 'a', 'second',
                    'season', '(', 'seventh', 'if', 'you', 'count', 'the', 'five', 'seasons', 'it', 'ran', 'on',
                    'Comedy', 'Central', 'from', '2000', 'to', '2002', ')', '.', 'And', 'they', "'ve",
                    'definitely', 'given', 'some', 'thought', 'as', 'to', 'what', 'they', "'d", 'like', 'to',
                    'do', 'similarly', 'and', 'what', 'they', "'d", 'like', 'to', 'change', 'up', '.']

        stop_words_removed = _remove_stop_words(document)

        words = ['this', 'that', 'at', 'the', 'a', 'is', 'are', 'was']
        self.assertTrue(all(x not in stop_words_removed for x in words))

    def test_filter_latin_words(self):
        words = ['I', 'know', 'how', 'to', 'do', 'it']
        self.assertTrue(words == _filter_latin_words(words))

        self.assertTrue(not _filter_latin_words(['1000']))

    def test_tokenize_from_html(self):
        directory = os.path.dirname(os.path.abspath(__file__))
        file_content = open(os.path.join(directory, 'scraper_documents/2015-08-01 18:00:22.926317_8.json')).read()
        html_content = jsonpickle.decode(file_content).html_content
        tokenizer = DocTokenizerFromHtml()
        tokenized = tokenizer.tokenize(html_content)

        self.assertTrue(len(tokenized) > 200)
        self.assertTrue('a' not in tokenized)  # no too common english words
        self.assertTrue('as' not in tokenized)
        self.assertTrue(word.lower() == word for word in tokenized)  # lower cases

    def test_tokenize_from_rawtext(self):
        tokenizer = DocTokenizerFromRawText()
        tokenized = tokenizer.tokenize('This is raw text tokenizer')

        # no too common english words
        self.assertTrue('this' not in tokenized)
        self.assertTrue('is' not in tokenized)
        self.assertTrue('raw' in tokenized)
        self.assertTrue('text' in tokenized)
        self.assertTrue('tokenizer' in tokenized)
        self.assertTrue(word.lower() == word for word in tokenized)  # lower cases


if __name__ == '__main__':
    unittest.main()
