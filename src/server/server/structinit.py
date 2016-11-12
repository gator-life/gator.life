# -*- coding: utf-8 -*-
from . import frontendstructs as struct
from . import passwordhelpers


def create_user_in_db(email, interests, password, dal):
    user = struct.User.make_from_scratch(email, interests)
    dal.user.save_user(user, passwordhelpers.hash_password(password))

    # Create an empty profile for the newly created user
    ref_feature_set_id = dal.feature_set.get_ref_feature_set_id()
    feature_set = dal.feature_set.get_feature_set(ref_feature_set_id)
    set_length = len(feature_set.feature_names)
    feature_vector = struct.FeatureVector.make_from_scratch([1] * set_length, feature_set.feature_set_id)
    model_data = struct.UserProfileModelData.make_empty(set_length)
    profile = struct.UserComputedProfile.make_from_scratch(feature_vector, model_data)

    dal.user_computed_profile.save_user_computed_profiles([(user, profile)])
    return user
