# -*- coding: utf-8 -*-

from common.datehelper import utcnow
from learner.userprofiler import UserProfiler, ActionOnDoc
import server.frontendstructs as struct
from server.dal import Dal


def update_profiles_in_database(users):
    """
    This method update profile in database of all users from their new actions since last model update
    """
    _update_profiles_in_database(users, UserProfiler(), utcnow())


def _update_profiles_in_database(users, profiler, now):
    if len(users) == 0:
        return  # no profile to update
    dal = Dal()
    old_profiles = dal.user_computed_profile.get_user_computed_profiles(users)
    actions_by_user = _get_new_actions(dal, users, old_profiles)
    new_profiles = _build_updated_profiles(profiler, zip(old_profiles, actions_by_user), now)
    dal.user_computed_profile.save_user_computed_profiles(zip(users, new_profiles))


def _get_new_actions(dal, users, old_profiles):
    # min requests date is unique for all users, we need to request all from this date
    min_datetime_request = min(old_profiles, key=lambda item: item.datetime).datetime
    return dal.user_action.get_user_actions_on_docs(users, min_datetime_request)


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
    new_feature_vector = struct.FeatureVector(new_profile.feedback_vector, feature_set_id)
    return struct.UserComputedProfile(new_feature_vector, new_profile.model_data)


def _to_action_in_profiler_format(action):
    return ActionOnDoc(action.datetime, action.document.feature_vector.vector, action.action_type)
