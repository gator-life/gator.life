#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import unittest
import math
import numpy as np
from learner.userprofiler import UserProfiler, ActionOnDoc, _ElementProfile
from userdocmatch.frontendstructs import UserActionTypeOnDoc, UserProfileModelData


class UserProfilerTests(unittest.TestCase):

    def test_compute_user_profile_initial(self):
        profiler = UserProfiler()
        profiler._decay_annual_rate = math.log(2)  # so that coeff is divided by 2 in one year
        previous_date = datetime(2020, 1, 1)
        doc_date1 = datetime(2021, 1, 1)
        intermediate_date = datetime(2021, 4, 1)
        doc_date2 = datetime(2022, 1, 1)
        new_date = datetime(2023, 1, 1)

        actions = [
            ActionOnDoc(doc_date1, [1.0, 1.0], UserActionTypeOnDoc.up_vote),
            ActionOnDoc(doc_date2, [1.0, 0.0], UserActionTypeOnDoc.click_link),
            ActionOnDoc(doc_date1, [0.0, 1.0], UserActionTypeOnDoc.down_vote),
            ActionOnDoc(doc_date2, [2.0, 1.0], UserActionTypeOnDoc.view_link),
        ]

        explicit_feedback_vec = [0.5, 2.0]
        init_model_data = UserProfileModelData(explicit_feedback_vec, [0.0, 0.0], [0.0, 0.0], 0.0, 0.0)
        new_profile = profiler.compute_user_profile(init_model_data, previous_date, actions, new_date)

        # Explicit feedback vector should not change
        self.assertEquals(new_profile.model_data.explicit_feedback_vector, init_model_data.explicit_feedback_vector)

        # --------1) test that profile computed from scratch gives the expected feature_vector angle
        # expected vector =
        # +pos_coeff*(up_doc*up_coeff/4 + click_doc*click_coeff/2)/(up_coeff/4+click_coeff/2)
        # -neg_coeff*(down_doc*down_coeff/4+view_doc*view_coeff/2)/(down_coeff/4+view_coeff/2)
        pos_factor = 0.8 / (5.0 / 4.0 + 1. / 2)
        neg_factor = 0.2 / (10.0 / 4.0 + 1. / 2)
        pos_vec = [5. / 4 + 1. / 2, 5. / 4]
        neg_vec = [2. / 2, 10. / 4 + 1. / 2]
        diff_pos_neg_vec = [pos_factor * pos_val - neg_factor * neg_val for pos_val, neg_val in zip(pos_vec, neg_vec)]

        # The new feedback vector should be at the average angle of position-negative vector and the explicit feedback vector
        expected_angle = (np.arctan2(explicit_feedback_vec[1], explicit_feedback_vec[0]) +
                          np.arctan2(diff_pos_neg_vec[1], diff_pos_neg_vec[0])) / 2
        new_angle = np.arctan2(new_profile.feedback_vector[1], new_profile.feedback_vector[0])
        self.assertAlmostEquals(expected_angle, new_angle, 3)

        # --------2) test the streaming process: the status (feature_vector and intermediate variables) should not
        #            change depending on the intermediate steps of computation
        first_step_action = [action for action in actions if action.datetime <= intermediate_date]
        second_step_action = [action for action in actions if action.datetime > intermediate_date]
        intermediate_profile = profiler.compute_user_profile(
            init_model_data, previous_date, first_step_action, intermediate_date)
        final_profile = profiler.compute_user_profile(
            intermediate_profile.model_data, intermediate_date, second_step_action, new_date)

        self.assert_profile_equals(new_profile, final_profile)

    def test_compute_global_feedback_vector_with_no_positive_feedback_only_use_negative(self):
        # If there is no positive feedback. The best we can do is using only negative feedback.
        # What really matters is the direction of the vector. Here in 2 dimensions, this is just the slope between
        # first and second axis
        profiler = UserProfiler()
        pos_elt = _ElementProfile(np.asarray([3.0, 3.0]), 0)
        neg_elt = _ElementProfile(np.asarray([5.0, 1.0]), 1)
        vector = profiler._compute_global_feedback_vector(np.asarray([0.0, 0.0]), neg_elt, pos_elt)
        self.assertEqual(5.0, vector[0] / vector[1])  # 'slope' of negative vector should be kept

    def test_compute_global_feedback_vector_with_no_negative_feedback_only_use_positive(self):
        # same logic as test_compute_global_feedback_vector_with_no_positive_feedback_only_use_negative
        profiler = UserProfiler()
        neg_elt = _ElementProfile(np.asarray([3.0, 3.0]), 0)
        pos_elt = _ElementProfile(np.asarray([5.0, 1.0]), 1)
        vector = profiler._compute_global_feedback_vector(np.asarray([0.0, 0.0]), neg_elt, pos_elt)
        self.assertEqual(5.0, vector[0] / vector[1])

    def test_compute_global_feedback_vector_with_only_explicit_vector(self):
        profiler = UserProfiler()
        neg_elt = _ElementProfile(np.asarray([0.0, 0.0]), 0)
        pos_elt = _ElementProfile(np.asarray([0.0, 0.0]), 0)
        vector = profiler._compute_global_feedback_vector(np.asarray([1.0, 1.5]), neg_elt, pos_elt)
        # Here again, what matters is the direction of the vector which should be the same as the the direction of explicit
        # feedback vector
        self.assertEqual(1.0 / 1.5, vector[0] / vector[1])

    def assert_profile_equals(self, expected, result):
        self.assert_model_data_equals(expected.model_data, result.model_data)
        self.assert_list_almost_equals(expected.feedback_vector, result.feedback_vector)

    def assert_model_data_equals(self, expected, result):
        self.assertAlmostEquals(expected.positive_feedback_sum_coeff, result.positive_feedback_sum_coeff)
        self.assertAlmostEquals(expected.negative_feedback_sum_coeff, result.negative_feedback_sum_coeff)
        self.assert_list_almost_equals(expected.explicit_feedback_vector, result.explicit_feedback_vector)
        self.assert_list_almost_equals(expected.positive_feedback_vector, result.positive_feedback_vector)
        self.assert_list_almost_equals(expected.negative_feedback_vector, result.negative_feedback_vector)

    def assert_list_almost_equals(self, expected, result, places=7):
        self.assertEquals(type(result), type([]))  # check result is a standard python list
        self.assertEquals(len(expected), len(result))
        for exp, res in zip(expected, result):
            self.assertAlmostEquals(exp, res, places)


if __name__ == '__main__':
    unittest.main()
