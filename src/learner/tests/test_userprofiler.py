from datetime import datetime
import unittest
import math
from learner.userprofiler import UserProfile, UserProfiler, ActionOnDoc
from server.frontendstructs import UserActionTypeOnDoc


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

        init_profile = UserProfile.make_empty(datetime=previous_date, vector_size=2)
        new_profile = profiler.compute_user_profile(init_profile, actions, new_date)

        # --------1) test that profile computed from scratch gives the expected feature_vector
        # expected vector =
        # +pos_coeff*(up_doc*up_coeff/4 + click_doc*click_coeff/2)/(up_coeff/4+click_coeff/2)
        # -neg_coeff*(down_doc*down_coeff/4+view_doc*view_coeff/2)/(down_coeff/4+view_coeff/2)
        pos_factor = 0.8/(5.0/4.0+0.5)
        neg_factor = 0.2/(10.0/4.0+1./2)
        pos_vec = [5./4+1./2, 5./4]
        neg_vec = [1.0, 10./4+1./2]

        expected_vec = [pos_factor*pos_val - neg_factor*neg_val for pos_val, neg_val in zip(pos_vec, neg_vec)]
        self.assertEquals(new_date, new_profile.datetime)
        self.assert_list_almost_equals(expected_vec, new_profile.global_feedback_vector, places=3)

        # --------2) test the streaming process: the status (feature_vector and intermediate variables) should not
        #            change depending on the intermediate steps of computation
        first_step_action = [action for action in actions if action.datetime <= intermediate_date]
        second_step_action = [action for action in actions if action.datetime > intermediate_date]
        intermediate_profile = profiler.compute_user_profile(init_profile, first_step_action, intermediate_date)
        final_profile = profiler.compute_user_profile(intermediate_profile, second_step_action, new_date)

        self.assert_profile_equals(new_profile, final_profile)

    def assert_profile_equals(self, expected, result):
        self.assertEquals(expected.datetime, result.datetime)
        self.assertAlmostEquals(expected.sum_coeff_positive_feedback, result.sum_coeff_positive_feedback)
        self.assertAlmostEquals(expected.sum_coeff_negative_feedback, result.sum_coeff_negative_feedback)
        self.assert_list_almost_equals(expected.positive_feedback_vector, result.positive_feedback_vector)
        self.assert_list_almost_equals(expected.negative_feedback_vector, result.negative_feedback_vector)
        self.assert_list_almost_equals(expected.global_feedback_vector, result.global_feedback_vector)

    def assert_list_almost_equals(self, expected, result, places=7):
        self.assertEquals(len(expected), len(result))
        for exp, res in zip(expected, result):
            self.assertAlmostEquals(exp, res, places)


if __name__ == '__main__':
    unittest.main()
