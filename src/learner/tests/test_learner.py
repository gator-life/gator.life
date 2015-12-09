#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from learner.learner import compute_user_doc_matching


class LearnerTests(unittest.TestCase):

    def test_compute_user_doc_matching_with_grade_above_should_flag_doc_as_relevant(self):

        user1_feature_vector = [0.49, 1.0, 0.0]
        user2_feature_vector = [0.5, 1.0, 0.1]

        user_feature_vectors = [user1_feature_vector, user2_feature_vector]

        matching = compute_user_doc_matching(
            user_feature_vectors=user_feature_vectors, document_feature_vector=[1.0, 0.5, 0.1], min_grade=1.0)

        self.assertFalse(matching[0].is_doc_relevant)
        self.assertEqual(0.99, matching[0].grade)
        self.assertTrue(matching[1].is_doc_relevant)
        self.assertEqual(1.01, matching[1].grade)


if __name__ == '__main__':
    unittest.main()
