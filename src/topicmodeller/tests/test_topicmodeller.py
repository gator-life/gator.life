#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import unittest

from topicmodeller.topicmodeller import TopicModeller


class TopicModellerTests(unittest.TestCase):

    class MockTokenizer(object):

        @classmethod
        def tokenize(cls, text):
            return [word for word in text.split() if word != 'is']

    def test_initialize_classify_save_load_classify_is_ok(self):
        doc1 = u'I like orange, i really love orange orange is my favorite color, green sucks'
        doc2 = u'Green is cool, green is nice, green is swag, orange not so much'
        docs = [doc1, doc2]

        topic_modeller = TopicModeller(self.MockTokenizer())
        topic_modeller._remove_optimizations = True  # pylint: disable=protected-access
        topic_modeller.initialize(docs, num_topics=2)

        # check number of topics is expected
        self.assertEquals(2, len(topic_modeller.topics))

        # check most recurrent words are selected topics (green, orange)
        index_orange = -1
        index_green = -1
        for index, topic in zip(range(2), topic_modeller.topics):
            (word, _) = topic[0]
            if word == u'orange':
                index_orange = index
            if word == u'green':
                index_green = index
        self.assertNotEquals(-1, index_orange)
        self.assertNotEquals(-1, index_green)

        # check classification is logical between doc1 and doc2 with two axes:
        # -same doc, different topic
        # -same topic, different docs
        (ok1, classification_after_init_doc1) = topic_modeller.classify(doc1)
        self.assertTrue(ok1)
        self.assertEquals(len(topic_modeller.topics), len(classification_after_init_doc1))
        (ok2, classification_after_init_doc2) = topic_modeller.classify(doc2)
        self.assertTrue(ok2)
        self.assertTrue(classification_after_init_doc1[index_orange] > classification_after_init_doc1[index_green])
        self.assertTrue(classification_after_init_doc2[index_orange] < classification_after_init_doc2[index_green])
        self.assertTrue(classification_after_init_doc1[index_orange] > classification_after_init_doc2[index_orange])
        self.assertTrue(classification_after_init_doc1[index_green] < classification_after_init_doc2[index_green])

        # check save then load model gives exact same classification for a document
        directory = os.path.dirname(os.path.abspath(__file__))
        topic_modeller.save(directory)

        deserialized_topic_modeller = TopicModeller(self.MockTokenizer())
        deserialized_topic_modeller.load(directory)

        (ok1_reload, classification_after_load_doc1) = deserialized_topic_modeller.classify(doc1)
        self.assertTrue(ok1_reload)
        self.assertEquals(len(topic_modeller.topics), len(classification_after_load_doc1))
        for after_init, after_load in zip(classification_after_init_doc1, classification_after_load_doc1):
            self.assertAlmostEqual(after_init, after_load, places=4)

    def test_topic_field(self):
        random.seed(0)

        words = ["word" + str(i) for i in range(150)]
        docs = []
        for _ in range(5):
            doc = ""
            for _ in range(150):
                doc += " " + random.choice(words)
            docs.append(doc)

        topic_modeller = TopicModeller(self.MockTokenizer())
        topic_modeller._remove_optimizations = True  # pylint: disable=protected-access
        topic_modeller.initialize(docs, num_topics=2)

        self.assertEquals(2, len(topic_modeller.topics))
        for topic in topic_modeller.topics:
            self.assertEquals(100, len(topic))
            for word, weight in topic:
                self.assertTrue(word in words)
                self.assertTrue(0 < weight < 1)


if __name__ == '__main__':
    unittest.main()
