#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scipy.spatial import distance
import numpy as np


class UserDocMatching(object):
    def __init__(self, is_doc_relevant, grade):
        self.is_doc_relevant = is_doc_relevant
        self.grade = grade


def compute_user_doc_matching(user_feature_vectors, document_feature_vector, min_grade):
    grade_vec = similarity_by_row(user_feature_vectors, document_feature_vector)
    return [UserDocMatching(is_doc_relevant=grade > min_grade, grade=grade) for grade in np.nditer(grade_vec)]


def similarity_by_row(matrix, vector):
    """
    compute the cosine similarity (normalized dot product) for each row of 'matrix' against 'vector'
    :param matrix: array of array or numpy matrix of dimension (n elements, p features)
    :param vector: vector of dimension p features
    :return: vector of size n
    """
    vec_as_1_p_matrix = [vector]
    return 1 - distance.cdist(matrix, vec_as_1_p_matrix, metric='cosine')
