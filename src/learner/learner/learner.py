#!/usr/bin/env python
# -*- coding: utf-8 -*-

from server.frontendstructs import Document, UserDocument

import jsonpickle
import os


def learn(documents_folder, min_grade):
    users = get_users()

    for file_name in os.listdir(documents_folder):
        file_path = os.path.join(documents_folder, file_name)
        file_content = open(file_path).read()

        topicmodeller_document = jsonpickle.decode(file_content)

        document = Document(topicmodeller_document.url, topicmodeller_document.title, None)

        save_document(document)

        learn_for_users(users, min_grade, document, topicmodeller_document.topics)


def learn_for_users(users, min_grade, document, topics):
    weights = [weight for (_, weight) in topics]
    for user in users:
        grade = sum(a * b for (a, b) in
                    zip(weights, user.feature_vector.vector))
        if grade > min_grade:
            user.user_docs.append(UserDocument(document, grade))


# Data Access Layer : Will be deleted
Documents = [] # pylint: disable=C0103
Users = [] # pylint: disable=C0103


def save_user(user):
    Users.append(user)


def get_users():
    return Users


def save_document(document):
    Documents.append(document)
