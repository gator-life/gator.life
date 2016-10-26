# -*- coding: utf-8 -*-
from .dal import REF_FEATURE_SET
from . import frontendstructs as struct
from . import passwordhelpers


def create_user_in_db(email, interests, password, dal):
    user = struct.User.make_from_scratch(email, interests)
    dal.user.save_user(user, passwordhelpers.hash_password(password))

    # Create an empty profile for the newly created user
    features_set = dal.feature_set.get_feature_set(REF_FEATURE_SET).feature_names
    feature_vector = struct.FeatureVector.make_from_scratch([1] * len(features_set), REF_FEATURE_SET)
    model_data = struct.UserProfileModelData.make_empty(len(features_set))
    profile = struct.UserComputedProfile.make_from_scratch(feature_vector, model_data)

    dal.user_computed_profile.save_user_computed_profiles([(user, profile)])
    return user
