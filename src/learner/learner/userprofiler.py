# -*- coding: utf-8 -*-

from math import e
import numpy as np
from server.frontendstructs import UserActionTypeOnDoc, UserProfileModelData


class ActionOnDoc(object):
    """
    Represent an action of a user as needed by the UserProfiler
    """

    def __init__(self, datetime, doc_feature_vector, action_type):
        """
        :param datetime: date of the action
        :param doc_feature_vector:  feature vector of the doc associated to this action
        :param action_type: type of action on the document
        :return:
        """
        self.datetime = datetime
        self.doc_feature_vector = doc_feature_vector
        self.action_type = action_type


class UserProfile(object):
    """
    User profile computed by profiler
    """

    def __init__(self, model_data, feedback_vector):
        """
        :param model_data: UserProfileModelData, intermediate variables needed by rocchio algorithm
        to compute feedback vector at each learning step in profiler
        :param feedback_vector: [float], computed feedback vector of the user
        """
        self.model_data = model_data
        self.feedback_vector = feedback_vector


class UserProfiler(object):
    """
    Class executing the algorithm to compute the User profile from the actions of this user
    """

    def __init__(self):
        self._positive_feedback_coeff = 0.8
        self._negative_feedback_coeff = 1.0 - self._positive_feedback_coeff
        self._decay_annual_rate = 1.0
        self._action_type_to_positive_coeff = {
            UserActionTypeOnDoc.up_vote: 5.0,
            UserActionTypeOnDoc.click_link: 1.0,
            UserActionTypeOnDoc.down_vote: 0.0,
            UserActionTypeOnDoc.view_link: 0.0
        }
        self._action_type_to_negative_coeff = {
            UserActionTypeOnDoc.up_vote: 0.0,
            UserActionTypeOnDoc.click_link: 0.0,
            UserActionTypeOnDoc.down_vote: 10.0,
            UserActionTypeOnDoc.view_link: 1.0
        }

    def compute_user_profile(self, previous_model_data, previous_datetime, actions_on_docs, new_datetime):
        """
        Compute user profile (feature vector plus intermediate values to iterate as the user execute new actions)
        This execute the Rocchio algorithm based on the Wikipedia article, tweaked for:
            -time decay: a document loose relevance relatively as time passes
                         it uses e**(-rt) because only this form allows streaming algorithm
                         (no recomputing of all actions since the beginning)
            -coefficients among positive actions set or negative actions set: to give more relevance to up vote that click...
        The result vector of the tweaked Rocchio algorithm is then angularly averaged with the explicit feedback vector.
        :param previous_model_data: previously UserProfileModelData by the profiler
        :param previous_datetime: datetime when previous_user_profile_model_data has been computed by the profiler
        :param actions_on_docs: list of action since previous computation of UserProfile
        :param new_datetime: now
        :return: updated userprofiler.UserProfile for new actions
        """

        # we compute separately the 2 elements (positive and negative) the we add them to get final feature vector
        pos_elt = self._compute_user_profile_elt(
            previous_vec=previous_model_data.positive_feedback_vector,
            previous_sum_coeff=previous_model_data.positive_feedback_sum_coeff,
            previous_date=previous_datetime,
            actions=actions_on_docs,
            new_date=new_datetime,
            action_to_coeff=self._action_type_to_positive_coeff
        )
        neg_elt = self._compute_user_profile_elt(
            previous_vec=previous_model_data.negative_feedback_vector,
            previous_sum_coeff=previous_model_data.negative_feedback_sum_coeff,
            previous_date=previous_datetime,
            actions=actions_on_docs,
            new_date=new_datetime,
            action_to_coeff=self._action_type_to_negative_coeff
        )
        global_vec = self._compute_global_feedback_vector(np.asarray(previous_model_data.explicit_feedback_vector),
                                                          neg_elt, pos_elt)

        updated_model_data = UserProfileModelData(previous_model_data.explicit_feedback_vector,
                                                  pos_elt.sum_vec.tolist(), neg_elt.sum_vec.tolist(),
                                                  pos_elt.sum_coeff, neg_elt.sum_coeff)

        return UserProfile(updated_model_data, global_vec.tolist())

    def _compute_global_feedback_vector(self, explicit_feedback_vec, neg_elt, pos_elt):
        weighted_normalized_pos_vec = self._positive_feedback_coeff * self._compute_normalized_vector(pos_elt)
        weighted_normalized_neg_vec = self._negative_feedback_coeff * self._compute_normalized_vector(neg_elt)
        diff_pos_neg_vec = weighted_normalized_pos_vec - weighted_normalized_neg_vec

        diff_pos_neg_vec_norm = np.linalg.norm(diff_pos_neg_vec)
        if diff_pos_neg_vec_norm == 0:
            diff_pos_neg_vec_norm = 1
        explicit_feedback_norm = np.linalg.norm(explicit_feedback_vec)
        if explicit_feedback_norm == 0:
            explicit_feedback_norm = 1

        global_vec = (diff_pos_neg_vec / diff_pos_neg_vec_norm + explicit_feedback_vec / explicit_feedback_norm) / 2

        return global_vec

    @staticmethod
    def _compute_normalized_vector(profile_elt):
        # An absence of any action on one side is characterized by a sum_coeff to zero.
        # when there is no action on one side (ie: no negative actions), the best we can do is to take only
        # the other side in account. The two vectors (positive, negative) are added, so neutral element is the zero vector
        if profile_elt.sum_coeff == 0:
            return np.zeros(len(profile_elt.sum_vec))
        else:
            return profile_elt.sum_vec / profile_elt.sum_coeff

    def _compute_user_profile_elt(self, previous_vec, previous_sum_coeff, previous_date, actions, new_date, action_to_coeff):
        """ compute user profile variables for one element (positive or negative).
        3 steps algorithms:
        -discount previous profile
        -compute profile for new actions
        -mix the two to gives updated profile element
        """
        size_vec = len(previous_vec)

        discounted_previous_elt = self._discount_profile_elt(previous_date, previous_sum_coeff, previous_vec, new_date)
        new_actions_elt = self._new_actions_profile_elt(action_to_coeff, actions, new_date, size_vec)
        updated_sum_coeff = discounted_previous_elt.sum_coeff + new_actions_elt.sum_coeff
        updated_vec = discounted_previous_elt.sum_vec + new_actions_elt.sum_vec
        return _ElementProfile(updated_vec, updated_sum_coeff)

    def _new_actions_profile_elt(self, action_to_coeff, actions, new_date, size_vec):
        new_vec = np.zeros(size_vec)
        new_sum_coeff = 0.0
        for action in actions:
            doc_discount_factor = _compute_discount_factor(self._decay_annual_rate, action.datetime, new_date)
            doc_coeff = doc_discount_factor * action_to_coeff[action.action_type]
            doc_vector = np.asarray(action.doc_feature_vector)
            doc_weighted_vector = doc_coeff * doc_vector
            new_sum_coeff += doc_coeff
            new_vec += doc_weighted_vector
        new_actions_elt = _ElementProfile(new_vec, new_sum_coeff)
        return new_actions_elt

    def _discount_profile_elt(self, previous_date, previous_sum_coeff, previous_vec, new_date):
        previous_vec = np.asarray(previous_vec)
        disc_factor = _compute_discount_factor(self._decay_annual_rate, previous_date, new_date)
        discounted_previous_sum_coeff = disc_factor * previous_sum_coeff
        discounted_previous_vec = disc_factor * previous_vec
        return _ElementProfile(discounted_previous_vec, discounted_previous_sum_coeff)


def _compute_discount_factor(annual_rate, start_date, end_date):
    time_incr = end_date - start_date
    time_incr_in_years = time_incr.days / 365.25
    return e**(-annual_rate * time_incr_in_years)


class _ElementProfile(object):

    def __init__(self, sum_vector, sum_coeff):
        self.sum_vec = sum_vector
        self.sum_coeff = sum_coeff
