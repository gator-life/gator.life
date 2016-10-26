# -*- coding: utf-8 -*-

from server.dal import Dal, REF_FEATURE_SET
from server.frontendstructs import FeatureSet
DAL = Dal()


def initialize_topicmodeller_and_db(topic_modeller, html_documents, tm_data_folder, num_topics):
    initialize_topicmodeller(topic_modeller, html_documents, tm_data_folder, num_topics)
    initialize_db(topic_modeller)


def initialize_topicmodeller(topic_modeller, html_documents, tm_data_folder, num_topics):
    topic_modeller.initialize(html_documents, num_topics)
    topic_modeller.save(tm_data_folder)


def initialize_with_existing_dict(topic_modeller, html_documents, tm_data_folder, num_topics):
    topic_modeller.load_dictionary(tm_data_folder)
    topic_modeller.initialize_model(html_documents, num_topics)
    topic_modeller.save_model(tm_data_folder)


def initialize_db(topic_modeller):
    feature_names = [words[0] for (_, words) in topic_modeller.topics]
    DAL.feature_set.save_feature_set(FeatureSet.make_from_scratch(REF_FEATURE_SET, feature_names))
