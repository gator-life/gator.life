#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Document(object):

    @staticmethod
    def make_from_db(url, title, summary, date, db_key):
        return Document(url, title, summary, date, db_key)

    @staticmethod
    def make_from_scratch(url, title, summary):
        return Document(url, title, summary, date=None, db_key=None)

    def __init__(self, url, title, summary, date, db_key):
        self.url = url
        self.title = title
        self._db_key = db_key
        self.summary = summary
        self.date = date


class UserDocument(object):

    @staticmethod
    def make_from_scratch(document, grade):
        return UserDocument(document, grade)

    @staticmethod
    def make_from_db(document, grade):
        return UserDocument(document, grade)

    def __init__(self, document, grade):
        self.document = document
        self.grade = grade


class User(object):

    @staticmethod
    def make_from_db(email, user_doc_set_db_key, feature_vector_db_key):
        return User(email, user_doc_set_db_key, feature_vector_db_key)

    @staticmethod
    def make_from_scratch(email):
        return User(email, None, None)

    def __init__(self, email, user_doc_set_db_key, feature_vector_db_key):
        self.email = email
        self._user_doc_set_db_key = user_doc_set_db_key
        self._feature_vector_db_key = feature_vector_db_key


class FeatureVector(object):

    @staticmethod
    def make_from_scratch(vector, feature_set_id):
        return FeatureVector(vector, feature_set_id)

    def __init__(self, vector, feature_set_id):
        self.vector = vector
        self.feature_set_id = feature_set_id
