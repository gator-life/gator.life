from datetime import datetime
import unittest
import math
import numpy as np
from learner.userprofiler import UserProfiler, ActionOnDoc, _ElementProfile
from server.frontendstructs import UserActionTypeOnDoc, UserProfileModelData


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

        init_model_data = UserProfileModelData.make_empty(2)
        new_profile = profiler.compute_user_profile(init_model_data, previous_date, actions, new_date)

        # --------1) test that profile computed from scratch gives the expected feature_vector
        # expected vector =
        # +pos_coeff*(up_doc*up_coeff/4 + click_doc*click_coeff/2)/(up_coeff/4+click_coeff/2)
        # -neg_coeff*(down_doc*down_coeff/4+view_doc*view_coeff/2)/(down_coeff/4+view_coeff/2)
        pos_factor = 0.8 / (5.0 / 4.0 + 0.5)
        neg_factor = 0.2 / (10.0 / 4.0 + 1. / 2)
        pos_vec = [5. / 4 + 1. / 2, 5. / 4]
        neg_vec = [1.0, 10. / 4 + 1. / 2]

        expected_vec = [pos_factor * pos_val - neg_factor * neg_val for pos_val, neg_val in zip(pos_vec, neg_vec)]
        self.assert_list_almost_equals(expected_vec, new_profile.feedback_vector, places=3)

        # --------2) test the streaming process: the status (feature_vector and intermediate variables) should not
        #            change depending on the intermediate steps of computation
        first_step_action = [action for action in actions if action.datetime <= intermediate_date]
        second_step_action = [action for action in actions if action.datetime > intermediate_date]
        intermediate_profile = profiler.compute_user_profile(
            init_model_data, previous_date, first_step_action, intermediate_date)
        final_profile = profiler.compute_user_profile(
            intermediate_profile.model_data, intermediate_date, second_step_action, new_date)

        self.assert_profile_equals(new_profile, final_profile)

    def test_compute_global_feedback_vector_with_zero_positive_coeff(self):
        profiler = UserProfiler()
        pos_elt = _ElementProfile(np.asarray([3.0, 3.0]), 0)
        neg_elt = _ElementProfile(np.asarray([5.0, 1.0]), 1)
        vector = profiler._compute_global_feedback_vector(neg_elt, pos_elt)
        self.assertEqual(5.0, vector[0]/vector[1])

    def test_compute_global_feedback_vector_with_zero_negative_coeff(self):
        profiler = UserProfiler()
        neg_elt = _ElementProfile(np.asarray([3.0, 3.0]), 0)
        pos_elt = _ElementProfile(np.asarray([5.0, 1.0]), 1)
        vector = profiler._compute_global_feedback_vector(neg_elt, pos_elt)
        self.assertEqual(5.0, vector[0]/vector[1])

    def assert_profile_equals(self, expected, result):
        self.assert_model_data_equals(expected.model_data, result.model_data)
        self.assert_list_almost_equals(expected.feedback_vector, result.feedback_vector)

    def assert_model_data_equals(self, expected, result):
        self.assertAlmostEquals(expected.positive_feedback_sum_coeff, result.positive_feedback_sum_coeff)
        self.assertAlmostEquals(expected.negative_feedback_sum_coeff, result.negative_feedback_sum_coeff)
        self.assert_list_almost_equals(expected.positive_feedback_vector, result.positive_feedback_vector)
        self.assert_list_almost_equals(expected.negative_feedback_vector, result.negative_feedback_vector)

    def assert_list_almost_equals(self, expected, result, places=7):
        self.assertEquals(type(result), type([]))  # check result is a standard python list
        self.assertEquals(len(expected), len(result))
        for exp, res in zip(expected, result):
            self.assertAlmostEquals(exp, res, places)


if __name__ == '__main__':
    unittest.main()
