#!/usr/bin/env python
# -*- coding: utf-8 -*-

from server.frontendstructs import Document, UserDocument

import jsonpickle
import os


def learn(documents_folder, min_grade):
    users = _get_users()

    for file_name in os.listdir(documents_folder):
        file_path = os.path.join(documents_folder, file_name)
        file_content = open(file_path).read()

        topicmodeller_document = jsonpickle.decode(file_content)

        document = Document(topicmodeller_document.url, topicmodeller_document.title, db_key=None)

        _save_document(document)

        _learn_for_users(users, min_grade, document, topicmodeller_document.topics)


def _learn_for_users(users, min_grade, document, topics):
    weights = [weight for (_, weight) in topics]
    for user in users:
        grade = sum(a * b for (a, b) in
                    zip(weights, user.feature_vector.vector))
        if grade > min_grade:
            user.user_docs.append(UserDocument(document, grade))


# Data Access Layer : Will be deleted
Documents = [] # pylint: disable=invalid-name
Users = [] # pylint: disable=invalid-name


def _save_user(user):
    Users.append(user)


def _get_users():
    return Users


def _save_document(document):
    Documents.append(document)
