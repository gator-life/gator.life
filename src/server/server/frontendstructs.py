#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Document(object):
    def __init__(self, url, title, db_key):
        self.url = url
        self.title = title
        self.db_key = db_key


class UserDocument(object):
    def __init__(self, document, grade):
        self.document = document
        self.grade = grade


class User(object):
    def __init__(self, email, user_docs, feature_vector):
        self.email = email
        self.user_docs = user_docs
        self.feature_vector = feature_vector


class FeatureVector(object):
    def __init__(self, vector, labels, feature_set_id):
        self.vector = vector
        self.labels = labels
        self.feature_set_id = feature_set_id
