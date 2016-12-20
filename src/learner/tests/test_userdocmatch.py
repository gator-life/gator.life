#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import sqrt
import unittest
from learner.userdocmatch import UserDocumentsAccumulator, UserData, UserDoc, _similarity_by_row, _FixedSizeHeap


def norm(vec):
    # test implementation of L2 norm without re-using numpy code
    return sqrt(sum(x * x for x in vec))


class LearnerTests(unittest.TestCase):

    def test_compute_user_doc_matching_with_grade_above_should_flag_doc_as_relevant(self):
        user1 = [0.49, 1.0, 0.0]
        user2 = [0.5, 1.0, 0.1]
        users = [user1, user2]
        doc = [1.0, 0.5, 0.1]
        matching = _similarity_by_row(matrix=users, vector=doc)
        self.assertIsInstance(matching[0], float)
        self.assertIsInstance(matching[1], float)
        self.assertEqual(0.99 / (norm(user1) * norm(doc)), matching[0])
        self.assertEqual(1.01 / (norm(user2) * norm(doc)), matching[1])


class FixedSizeHeapTests(unittest.TestCase):

    def test_push(self):

        def assert_equal(expected_key_value_tuple, heap_list_elt):
            self.assertEqual(expected_key_value_tuple, (heap_list_elt[0], heap_list_elt[-1]))

        def assert_in(expected_key_value_tuple, heap_list):
            self.assertTrue(expected_key_value_tuple in ((elt[0], elt[-1])for elt in heap_list))

        # create generator to make sure heap does not rely on structure of input (double iteration, side-effect in input...)
        input_list = (pair for pair in [(0.5, "A"), (0.2, "minInit"), (0.9, "B")])
        heap = _FixedSizeHeap(input_list, 4)
        # below max size, all elements should be presents
        self.assertEqual(3, len(heap.list))
        assert_equal((0.2, "minInit"), heap.list[0])
        heap.push(0.8, "C")
        self.assertEqual(4, len(heap.list))
        assert_equal((0.2, "minInit"), heap.list[0])
        # we add a better value than 0.2, this should move "minInit" out of heap
        heap.push(0.21, "D")
        self.assertEqual(4, len(heap.list))
        assert_equal((0.21, "D"), heap.list[0])
        heap.push(0.20, "notAdded")
        # check final state, in an heap, first is always min but it's not sorted
        self.assertEqual(4, len(heap.list))
        assert_equal((0.21, "D"), heap.list[0])
        assert_in((0.5, "A"), heap.list)
        assert_in((0.9, "B"), heap.list)
        assert_in((0.8, "C"), heap.list)


class UserDocumentsAccumulatorTest(unittest.TestCase):

    def test_init_then_add_docs_then_build_user_docs(self):
        vec1 = [-1.0, 1.0]
        vec2 = [1.0, -1.0]
        user_docs1 = (user_doc for user_doc in [UserDoc("doc1", 100)])
        user_docs2 = (user_doc for user_doc in [UserDoc("delete", -1), UserDoc("doc2", 0.0), UserDoc("doc3", 100)])
        user_data1 = UserData(vec1, user_docs1)
        user_data2 = UserData(vec2, user_docs2)
        user_data_list = (data for data in [user_data1, user_data2])
        accumulator = UserDocumentsAccumulator(user_data_list, 2)

        def assert_user_docs(expected_list_docs, result_list_user_docs):
            self.assertEqual(len(expected_list_docs), len(result_list_user_docs))
            for result in result_list_user_docs:
                self.assertTrue(result.doc_id in expected_list_docs)

        result_users_docs = accumulator.build_user_docs()
        assert_user_docs(["doc1"], result_users_docs[0])
        assert_user_docs(["doc2", "doc3"], result_users_docs[1])  # max size 2, less relevant "delete" removed

        accumulator.add_doc("doc4", [10.0, 0.0])
        result2_users_docs = accumulator.build_user_docs()
        assert_user_docs(["doc1", "doc4"], result2_users_docs[0])  # doc4 relevant for the first user because it's not full
        assert_user_docs(["doc3", "doc4"], result2_users_docs[1])  # doc4 relevant for the second user, exclude doc2

        accumulator.add_doc("doc5", [0.0, 10.0])
        result3_users_docs = accumulator.build_user_docs()
        assert_user_docs(["doc1", "doc5"], result3_users_docs[0])  # doc5 relevant only for user1, and excludes doc4
        assert_user_docs(["doc3", "doc4"], result3_users_docs[1])  # user2 remains the same


if __name__ == '__main__':
    unittest.main()
