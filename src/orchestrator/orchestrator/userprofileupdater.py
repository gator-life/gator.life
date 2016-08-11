#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from common.datehelper import utcnow
from learner.userprofiler import UserProfiler, ActionOnDoc
import server.frontendstructs as struct
from server.dal import Dal

DAL = Dal()


def update_profiles_in_database(user_profiler=UserProfiler()):
    """
    This method update profile in database of all users from their new actions since last model update
    """
    _update_profiles_in_database(DAL.get_all_users(), user_profiler, utcnow())


def _update_profiles_in_database(users, profiler, now):
    old_profiles = DAL.get_user_computed_profiles(users)
    actions_by_user = _get_new_actions(users, old_profiles)
    new_profiles = _build_updated_profiles(profiler, zip(old_profiles, actions_by_user), now)
    DAL.save_computed_user_profiles(zip(users, new_profiles))


def _get_new_actions(users, old_profiles):
    # min requests date is unique for all users, we need to request all from this date
    min_datetime_request = min(old_profiles, key=lambda item: item.datetime).datetime
    return DAL.get_user_actions_on_docs(users, min_datetime_request)


def _build_updated_profiles(profiler, old_profile_to_actions_list, now):
    new_profiles = []
    for profile, actions in old_profile_to_actions_list:
        new_profile = _compute_new_user_profile(profiler, profile, actions, now)
        new_profiles.append(new_profile)
    return new_profiles


def _compute_new_user_profile(profiler, old_profile, user_actions, now):
    # as dal request has been done with a global min date, we must filter further for this specific user
    new_actions = (action for action in user_actions if action.datetime >= old_profile.datetime)
    actions_profiler_format = (_to_action_in_profiler_format(action) for action in new_actions)
    new_profile = profiler.compute_user_profile(old_profile.model_data, old_profile.datetime, actions_profiler_format, now)
    feature_set_id = old_profile.feature_vector.feature_set_id
    new_feature_vector = _compute_new_feature_vector(feature_set_id, old_profile.initial_feature_vector.vector,
                                                     new_profile.feedback_vector)
    return struct.UserComputedProfile.make_from_scratch(old_profile.initial_feature_vector, new_feature_vector,
                                                        new_profile.model_data)


def _compute_new_feature_vector(feature_set_id, initial_feature_vector, feedback_vector):
    initial_feature_vec_norm = _compute_vector_norm(initial_feature_vector)
    if initial_feature_vec_norm == 0:
        initial_feature_vec_norm = 1
    feedback_vec_norm = _compute_vector_norm(feedback_vector)
    if feedback_vec_norm == 0:
        feedback_vec_norm = 1

    new_feature_vec = [(x / initial_feature_vec_norm + y / feedback_vec_norm) / 2
                       for (x, y) in zip(initial_feature_vector, feedback_vector)]

    return struct.FeatureVector.make_from_scratch(new_feature_vec, feature_set_id)


def _compute_vector_norm(vector):
    return math.sqrt(sum([x*x for x in vector]))


def _to_action_in_profiler_format(action):
    return ActionOnDoc(action.datetime, action.document.feature_vector.vector, action.action_type)
