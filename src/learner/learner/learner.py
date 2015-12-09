#!/usr/bin/env python
# -*- coding: utf-8 -*-


class UserDocMatching(object):
    def __init__(self, is_doc_relevant, grade):
        self.is_doc_relevant = is_doc_relevant
        self.grade = grade


def compute_user_doc_matching(user_feature_vectors, document_feature_vector, min_grade):
    users_doc_matching = []
    for user_feature_vector in user_feature_vectors:
        grade = sum(a * b for (a, b) in zip(user_feature_vector, document_feature_vector))
        users_doc_matching.append(UserDocMatching(is_doc_relevant=grade > min_grade, grade=grade))
    return users_doc_matching
