# -*- coding: utf-8 -*-
import common.crypto as crypto
from common.datehelper import utcnow
from learner.topicmodelapprox import TopicModelApproxClassifier
from learner.userprofiler import UserProfiler
import nltk
from . import frontendstructs as struct


class UserCreator(object):

    def __init__(self):
        self._profile_initializer = None

    def create_user_in_db(self, email, interests, password, dal):
        if self._profile_initializer is None:
            self._profile_initializer = _get_profile_initializer(dal)

        user = struct.User.make_from_scratch(email, interests)
        profile = self._profile_initializer.get_new_profile(interests)
        dal.user.save_user(user, crypto.hash_password(password))
        dal.user_computed_profile.save_user_computed_profiles([(user, profile)])
        return user


def _get_profile_initializer(dal):
    ref_feature_set_id = dal.feature_set.get_ref_feature_set_id()
    feature_set = dal.feature_set.get_feature_set(ref_feature_set_id)
    model = dal.topic_model.get(feature_set.model_id)
    return _ProfileInitializer(ref_feature_set_id, model)


class _ProfileInitializer(object):

    def __init__(self, ref_feature_set_id, model_description):
        self._ref_feature_set_id = ref_feature_set_id
        self._classifier = TopicModelApproxClassifier(model_description)
        self._profiler = UserProfiler()
        self._nb_topics = len(model_description.topics)

    def get_new_profile(self, interests):
        words = []
        for sentence in interests:
            words_this_sentence = nltk.word_tokenize(sentence)
            words += [word.lower()for word in words_this_sentence]
        explicit_vector = self._classifier.compute_classified_vector(words)
        zero_vec = [0] * self._nb_topics
        model_data = struct.UserProfileModelData.make_from_scratch(explicit_vector, zero_vec, zero_vec, 0, 0)
        now = utcnow()
        profile = self._profiler.compute_user_profile(model_data, now, [], now)
        feature_vector = struct.FeatureVector.make_from_scratch(profile.feedback_vector, self._ref_feature_set_id)
        user_profile = struct.UserComputedProfile.make_from_scratch(feature_vector, profile.model_data)
        return user_profile
