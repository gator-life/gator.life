#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topicmodeller.topicmodeller import *

import unittest


document = 'Chinese (汉语 / 漢語; Hànyǔ or 中文; Zhōngwén) is a group of related but in many cases mutually unintelligible ' \
           'language varieties, forming a branch of the Sino-Tibetan language family. Chinese is spoken by the Han majority ' \
           'and many other ethnic groups in China. Nearly 1.2 billion people (around 16% of the world\'s population) speak ' \
           'some form of Chinese as their first language.'


class TopicModellerTests(unittest.TestCase):
    def test_readable_document(self):
        self.assertTrue(True)

    def test_word_tokenize(self):
        self.assertTrue(True)

    def test_remove_stop_words(self):
        self.assertTrue(True)

    def test_filter_latin_words(self):
        self.assertTrue(True)

# if __name__ == '__main__':
#     unittest.main()

