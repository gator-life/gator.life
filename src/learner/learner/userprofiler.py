#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import e
import numpy as np
from server.frontendstructs import UserActionTypeOnDoc


class UserProfile(object):
    """
    Represent the information about the profile:
    -global_feedback_vector is the vector to compute the interest of the user for a document in a VSM (Vector Space Model)
    -the others fields are the intermediate variables to compute this vector at each learning step in Rocchio algorithm
    """

    def __init__(self, datetime, sum_coeff_positive_feedback, sum_coeff_negative_feedback, positive_feedback_vector,
                 negative_feedback_vector, global_feedback_vector):
        self.datetime = datetime
        self.sum_coeff_positive_feedback = sum_coeff_positive_feedback
        self.sum_coeff_negative_feedback = sum_coeff_negative_feedback
        self.positive_feedback_vector = positive_feedback_vector
        self.negative_feedback_vector = negative_feedback_vector
        self.global_feedback_vector = global_feedback_vector

    @staticmethod
    def make_empty(datetime, vector_size):
        """
        Initialize an empty structure for a user without any actions yet
        :param datetime:
        :param vector_size:
        :return: UserProfile
        """
        return UserProfile(datetime, 0.0, 0.0, [0.0] * vector_size, [0.0] * vector_size, [1.0] * vector_size)


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

    def compute_user_profile(self, previous_user_profile, action_on_docs, datetime):
        """
        Compute user profile (feature vector plus intermediate values to iterate as the user execute new actions)
        This execute the Rocchio algorithm based on the Wikipedia article, tweaked for:
            -time decay: a document loose relevance relatively as time passes
                         it uses e**(-rt) because only this form allows streaming algorithm
                         (no recomputing of all actions since the beginning)
            -coefficients among positive actions set or negative actions set: to give more relevance to up vote that click...
        :param previous_user_profile: previous UserProfile
        :param action_on_docs: list of action since previous computation of UserProfile
        :param datetime: now
        :return: updated UserProfile for new actions
        """

        # we compute separately the 2 elements (positive and negative) the we add them to get final feature vector
        pos_elt = self._compute_user_profile_elt(
            previous_vec=previous_user_profile.positive_feedback_vector,
            previous_sum_coeff=previous_user_profile.sum_coeff_positive_feedback,
            previous_date=previous_user_profile.datetime,
            actions=action_on_docs,
            new_date=datetime,
            action_to_coeff=self._action_type_to_positive_coeff
        )
        neg_elt = self._compute_user_profile_elt(
            previous_vec=previous_user_profile.negative_feedback_vector,
            previous_sum_coeff=previous_user_profile.sum_coeff_negative_feedback,
            previous_date=previous_user_profile.datetime,
            actions=action_on_docs,
            new_date=datetime,
            action_to_coeff=self._action_type_to_negative_coeff
        )

        weighted_normalized_pos_vec = self._positive_feedback_coeff * pos_elt.sum_vec / pos_elt.sum_coeff
        weighted_normalized_neg_vec = self._negative_feedback_coeff * neg_elt.sum_vec / neg_elt.sum_coeff
        global_vec = weighted_normalized_pos_vec - weighted_normalized_neg_vec

        return UserProfile(
            datetime, pos_elt.sum_coeff, neg_elt.sum_coeff, pos_elt.sum_vec, neg_elt.sum_vec, global_vec)

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
