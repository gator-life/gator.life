#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import sqrt
import unittest
from learner.learner import compute_user_doc_matching


# test implementation of L2 norm without re-using numpy code
def norm(vec):
    return sqrt(sum(x*x for x in vec))


class LearnerTests(unittest.TestCase):

    def test_compute_user_doc_matching_with_grade_above_should_flag_doc_as_relevant(self):
        user1 = [0.49, 1.0, 0.0]
        user2 = [0.5, 1.0, 0.1]
        users = [user1, user2]
        doc = [1.0, 0.5, 0.1]

        matching = compute_user_doc_matching(user_feature_vectors=users, document_feature_vector=doc, min_grade=0.8)

        self.assertFalse(matching[0].is_doc_relevant)
        self.assertEqual(0.99/(norm(user1)*norm(doc)), matching[0].grade)
        self.assertTrue(matching[1].is_doc_relevant)
        self.assertEqual(1.01/(norm(user2)*norm(doc)), matching[1].grade)


if __name__ == '__main__':
    unittest.main()
