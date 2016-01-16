#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Document(object):

    @staticmethod
    def make_from_db(url, title, summary, datetime, db_key):
        return Document(url, title, summary, datetime, db_key)

    @staticmethod
    def make_from_scratch(url, title, summary):
        return Document(url, title, summary, datetime=None, db_key=None)

    def __init__(self, url, title, summary, datetime, db_key):
        self.url = url
        self.title = title
        self._db_key = db_key
        self.summary = summary
        self.datetime = datetime


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

# NB: when we manage dependencies in server, we can reference enum34 and make this class an enum
class UserActionTypeOnDoc(object):
    up_vote = 1
    down_vote = 2
    click_link = 3
    view_link = 4

class UserActionOnDoc(object):

    @staticmethod
    def make_from_scratch(document, action_type):
        return UserActionOnDoc(document, action_type, datetime=None)

    @staticmethod
    def make_from_db(document, action_type, datetime):
        return UserActionOnDoc(document, action_type, datetime)

    def __init__(self, document, action_type, datetime):
        self.document = document
        self.action_type = action_type
        self.datetime = datetime

