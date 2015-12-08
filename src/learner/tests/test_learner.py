#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from learner.learner import learn_for_users
from server.frontendstructs import Document, FeatureVector, User


class LearnerTests(unittest.TestCase):
    @classmethod
    def create_user(cls, feature_vector):
        feature_vector = FeatureVector(vector=feature_vector, labels=[], feature_set_id=None)
        user = User(u'', [], feature_vector)
        return user

    @classmethod
    def create_document(cls):
        return Document.make_from_scratch(url=u'', title=u'', summary=None)

    def create_users_documents_and_learn(self, users_feature_vector, min_grade, documents_topics):
        users = [self.create_user(feature_vector) for feature_vector in users_feature_vector]

        document_and_topics = [(self.create_document(), topics) for topics in documents_topics]

        for (document, topics) in document_and_topics:
            learn_for_users(users=users, document=document, topics=topics, min_grade=min_grade)

        return (users, [document for (document, topics) in document_and_topics])

    def test_associate_document(self):
        (users, documents) = self.create_users_documents_and_learn(
            users_feature_vector=[[0, 1, 0, 0]],
            min_grade=0.5,
            documents_topics=[[(1, 0), (2, 0.6), (3, 0), (4, 0)]])

        self.assertIn(documents[0], [user_doc.document for user_doc in users[0].user_docs])

    def test_associate_each_document_to_one_user(self):
        (users, documents) = self.create_users_documents_and_learn(
            users_feature_vector=[[0, 1, 0, 0.05], [0, 0.1, 0, 0.8]],
            min_grade=0.5,
            documents_topics=[[(1, 0), (2, 0.6), (3, 0), (4, 0)], [(1, 0), (2, 0), (3, 0), (4, 0.7)]])

        for (user, document) in zip(users, documents):
            self.assertIn(document, [user_doc.document for user_doc in user.user_docs])

        users.reverse()
        for (user, document) in zip(users, documents):
            self.assertNotIn(document, [user_doc.document for user_doc in user.user_docs])

    def test_associate_document_to_multiple_users(self):
        (users, documents) = self.create_users_documents_and_learn(
            users_feature_vector=[[0, 0.9, 0, 0.05], [0, 0.2, 0, 0.4]],
            min_grade=0.49,
            documents_topics=[[(1, 0), (2, 0.5), (3, 0), (4, 1)]])

        for user in users:
            self.assertIn(documents[0], [user_doc.document for user_doc in user.user_docs])

    def test_do_not_associate_document_min_grade_high(self):
        (users, documents) = self.create_users_documents_and_learn(
            users_feature_vector=[[0, 1, 0, 0]],
            min_grade=1,
            documents_topics=[[(1, 0), (2, 0.6), (3, 0), (4, 0)]])

        self.assertNotIn(documents[0], [user_doc.document for user_doc in users[0].user_docs])

    def test_do_not_associate_document_grade_inf_min_grade(self):
        (users, documents) = self.create_users_documents_and_learn(
            users_feature_vector=[[1, 1, 0, 0]],
            min_grade=0.5,
            documents_topics=[[(1, 0.1), (2, 0.3), (3, 0), (4, 0)]])

        self.assertNotIn(documents[0], [user_doc.document for user_doc in users[0].user_docs])

if __name__ == '__main__':
    unittest.main()
