#!/usr/bin/env python
# -*- coding: utf-8 -*-
import heapq
from scipy.spatial import distance
import numpy as np


class UserDoc(object):
    def __init__(self, doc_id, grade):
        """
        :param doc_id: object whose reference is used as identifier of a document, concrete type does not matter and can be
        anything that the client see fit
        :param grade: computed grade of the document for the user
        """
        self.doc_id = doc_id
        self.grade = grade


class UserData(object):
    def __init__(self, feature_vector, user_docs):
        """
        :param feature_vector: feature_vector of the user (double array)
        :param user_docs: list of most relevant (top rated) doc for the user (UserDoc list)
        """
        self.feature_vector = feature_vector
        self.user_docs = user_docs


class UserDocumentsAccumulator(object):

    def __init__(self, user_data_list, user_docs_max_size):
        """
        :param user_data_list: list of learner.UserData, UserData.feature_vector must have the same size of feature_vector
        of documents that will be added
        :param user_docs_max_size: max number of documents to add in userDocs for each user (int)
        """
        self._user_docs_heaps = []
        user_feature_vectors = []
        for data in user_data_list:
            grade_doc_list = ((doc.grade, doc.doc_id) for doc in data.user_docs)
            user_docs_heap = _FixedSizeHeap(key_value_list=grade_doc_list, max_size=user_docs_max_size)
            self._user_docs_heaps.append(user_docs_heap)
            user_feature_vectors.append(data.feature_vector)
        self._user_feature_vector_matrix = np.matrix(user_feature_vectors)

    def add_doc(self, doc_id, feature_vector):
        """
        NB: The computational cost for each doc is:
        O(
           nb_users --> iterate on all user heaps
           +
           nb_users*log(user_docs_max_size)*Proba(doc relevant for user)) --> add in heaps
           +
           nb_user*nb_features --> matrix multiplication
        )
        :param doc_id:
        :param feature_vector:
        """
        grade_vec = _similarity_by_row(self._user_feature_vector_matrix, feature_vector)
        for grade, user_docs_heap in zip(grade_vec, self._user_docs_heaps):
            user_docs_heap.push(grade, doc_id)

    def build_user_docs(self):
        """
        :return: a list, where each index match the user in user_data_list __init__ parameter.
        Each element is the list of the top rated learner.UserDoc, of length <= user_docs_max_size.
        Those lists take in account all the documents added by the add_doc method
        """
        return [[UserDoc(doc, grade) for (grade, doc) in heap.list] for heap in self._user_docs_heaps]


def _similarity_by_row(matrix, vector):
    """
    compute the cosine similarity (normalized dot product) for each row of 'matrix' against 'vector'
    :param matrix: array of array or numpy matrix of dimension (n elements, p features)
    :param vector: vector of dimension p features
    :return: vector of size n
    """
    vec_as_1_p_matrix = [vector]
    return 1 - distance.cdist(matrix, vec_as_1_p_matrix, metric='cosine')


class _FixedSizeHeap(object):
    """
    Min Heap data structure with a fixed size. It means at each instant, you keep the "max_size" biggest elements
    based on the comparison of the keys.
    If len(heap.list)==max_size, adding a new element
        -won't change anything if key<min(list)
        -will remove the minimum present element and add replace it by the new element in the list
    """
    def __init__(self, key_value_list, max_size):
        self._max_size = max_size
        self.list = []
        for (key, value) in key_value_list:
            self.push(key, value)

    def push(self, key, value):
        if len(self.list) < self._max_size:
            heapq.heappush(self.list, (key, value))
        else:
            heapq.heappushpop(self.list, (key, value))
