# -*- coding: utf-8 -*-

from server.dal import Dal
from server.frontendstructs import FeatureSet, UserProfileModelData, UserComputedProfile, FeatureVector, Document,\
    TopicModelDescription
from learner.topic_model_converter import TopicModelConverter
from learner.userprofiler import UserProfiler


class ModelUpdater(object):

    @staticmethod
    def update_model_in_db(topic_modeller, all_users):
        """
        NB: all_users must be "all" because function will modify documents in database and if others users are using those
        same docs, it will create a mismatch of vector model between those other users and updated docs
        """
        dal = Dal()

        model_id = topic_modeller.get_model_id()
        if _is_already_ref(dal, model_id):
            return

        target_model = TopicModelDescription.make_from_scratch(model_id, topic_modeller.get_topics())
        target_feature_set_id = target_model.topic_model_id
        _save_topic_model_and_feature_set(dal, target_model)

        profiles = dal.user_computed_profile.get_user_computed_profiles(all_users)
        feature_set_ids = list(set(profile.feature_vector.feature_set_id for profile in profiles))
        converter_dict = _get_model_converters(dal, feature_set_ids, target_model)

        user_to_profile = zip(all_users, profiles)
        updated_user_to_profiles = _get_updated_user_to_profile(converter_dict, user_to_profile, target_feature_set_id)
        dal.user_computed_profile.save_user_computed_profiles(updated_user_to_profiles)

        user_docs_by_user = dal.user_doc.get_users_docs(all_users)
        # No need to update all docs in db, only those reachable by at least one user
        docs = set(user_doc.document for user_docs in user_docs_by_user for user_doc in user_docs)
        updated_docs = _get_updated_docs(docs, converter_dict, target_feature_set_id)
        dal.doc.save_documents(updated_docs)


def _is_already_ref(dal, topic_model_id):
    ref_feature_set_id = dal.feature_set.get_ref_feature_set_id()
    feature_set = dal.feature_set.get_feature_set(ref_feature_set_id)
    return feature_set.model_id == topic_model_id


def _save_topic_model_and_feature_set(dal, model):  # pylint: disable=invalid-name
    dal.topic_model.save(model)
    target_feature_names = [topic.topic_words[0].word for topic in model.topics]
    dal.feature_set.save_ref_feature_set_id(model.topic_model_id)
    target_feature_set = FeatureSet.make_from_scratch(model.topic_model_id, target_feature_names, model.topic_model_id)
    dal.feature_set.save_feature_set(target_feature_set)


def _get_model_converters(dal, feature_set_ids, target_model):
    feature_sets = [dal.feature_set.get_feature_set(feature_set_id) for feature_set_id in feature_set_ids]
    models = [dal.topic_model.get(feature_set.model_id) for feature_set in feature_sets]
    model_converters = [TopicModelConverter(model, target_model) for model in models]
    return dict(zip(feature_set_ids, model_converters))


def _get_updated_docs(docs, feature_set_id_to_converter, target_feature_set_id):
    updated_docs = []
    for doc in docs:
        feature_set_id = doc.feature_vector.feature_set_id
        if feature_set_id == target_feature_set_id:
            continue
        converter = feature_set_id_to_converter[feature_set_id]
        target_vector = converter.compute_target_vector(doc.feature_vector.vector)
        target_feature_vector = FeatureVector.make_from_scratch(target_vector, target_feature_set_id)
        updated_doc = Document.make_from_db(
            doc.url, doc.url_hash, doc.title, doc.summary, doc.datetime, target_feature_vector)
        updated_docs.append(updated_doc)
    return updated_docs


def _get_updated_user_to_profile(feature_set_id_to_converter, user_to_profile, target_feature_set_id):
    user_profiler = UserProfiler()
    updated_user_to_profile = []
    for user, profile in user_to_profile:
        feature_set_id = profile.feature_vector.feature_set_id
        if feature_set_id == target_feature_set_id:
            continue
        converter = feature_set_id_to_converter[feature_set_id]
        model_data_target = _get_updated_model_data(converter, profile.model_data)

        profiler_profile = user_profiler.compute_user_profile(model_data_target, profile.datetime, [], profile.datetime)
        target_feature_vector = FeatureVector.make_from_scratch(profiler_profile.feedback_vector, target_feature_set_id)
        target_profile = UserComputedProfile.make_from_db(
            target_feature_vector, model_data_target, profile.datetime)

        updated_user_to_profile.append((user, target_profile))
    return updated_user_to_profile


def _get_updated_model_data(converter, model_data_origin):
    explicit_target = converter.compute_target_vector(model_data_origin.explicit_feedback_vector)
    positive_target = converter.compute_target_vector(model_data_origin.positive_feedback_vector)
    negative_target = converter.compute_target_vector(model_data_origin.negative_feedback_vector)
    model_data_target = UserProfileModelData.make_from_scratch(
        explicit_target, positive_target, negative_target,
        model_data_origin.positive_feedback_sum_coeff, model_data_origin.negative_feedback_sum_coeff)
    return model_data_target
