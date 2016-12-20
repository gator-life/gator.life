# -*- coding: utf-8 -*-
import datetime
import logging
import common.crypto as crypto
from common.datehelper import utcnow
from learner.topicmodelapprox import TopicModelApproxClassifier
from learner.userprofiler import UserProfiler
from learner.userdocmatch import UserDocumentsAccumulator, UserData
import nltk
from . import frontendstructs as struct


LOGGER = logging.getLogger(__name__)


class UserCreator(object):

    def __init__(self):
        self._profile_initializer = None
        self._doc_duration = datetime.timedelta(hours=12)
        self._nb_user_docs = 30

    def create_user_in_db(self, email, interests, password, dal):
        if self._profile_initializer is None:
            self._profile_initializer = _get_profile_initializer(dal)

        user = struct.User.make_from_scratch(email, interests)
        profile = self._profile_initializer.get_new_profile(interests)
        user_docs = _get_user_docs(dal, profile.feature_vector, utcnow() - self._doc_duration, self._nb_user_docs)
        dal.user.save_user(user, crypto.hash_password(password))
        dal.user_computed_profile.save_user_computed_profiles([(user, profile)])
        dal.user_doc.save_user_docs(user, user_docs)
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
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug('tokenize interests [%s]', '-'.join(interests))
        for sentence in interests:
            words_this_sentence = nltk.word_tokenize(sentence)
            words += [word.lower()for word in words_this_sentence]
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug('classify interests [%s]', '-'.join(words))
        explicit_vector = self._classifier.compute_classified_vector(words)
        zero_vec = [0] * self._nb_topics
        model_data = struct.UserProfileModelData(explicit_vector, zero_vec, zero_vec, 0, 0)
        now = utcnow()
        profile = self._profiler.compute_user_profile(model_data, now, [], now)
        feature_vector = struct.FeatureVector(profile.feedback_vector, self._ref_feature_set_id)
        user_profile = struct.UserComputedProfile(feature_vector, profile.model_data)
        return user_profile


def _get_user_docs(dal, user_feature_vector, min_date_docs, nb_user_docs):
    # limit to 1000 so we can call dal.doc.get_docs (fails above 1000 in datastore)
    LOGGER.debug('get user docs, nb_user_docs[%s] min_date_docs[%s]', nb_user_docs, min_date_docs)
    docs = dal.doc.get_recent_docs(min_date_docs, max_nb_docs=1000)
    user_feat_set_id = user_feature_vector.feature_set_id
    valid_docs = [doc for doc in docs if doc.feature_vector.feature_set_id == user_feat_set_id]
    LOGGER.debug('accumulate docs, nb valid_docs[%s]', len(valid_docs))
    doc_accu = UserDocumentsAccumulator([UserData(user_feature_vector.vector, [])], nb_user_docs)
    for doc in valid_docs:
        doc_accu.add_doc(doc, doc.feature_vector.vector)
    lrn_docs = doc_accu.build_user_docs()[0]
    to_user_doc = lambda lrn_doc: struct.UserDocument(lrn_doc.doc_id, lrn_doc.grade)
    user_docs = [to_user_doc(lrn_doc) for lrn_doc in lrn_docs]
    return user_docs
