#!/usr/bin/env python
# -*- coding: utf-8 -*-

from server.frontendstructs import UserDocument


def learn_for_users(users, document, topics, min_grade):
    weights = [weight for (_, weight) in topics]
    for user in users:
        grade = sum(a * b for (a, b) in
                    zip(weights, user.feature_vector.vector))
        if grade > min_grade:
            user.user_docs.append(UserDocument(document, grade))
