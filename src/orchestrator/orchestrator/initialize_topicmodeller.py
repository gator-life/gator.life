# -*- coding: utf-8 -*-


def initialize_topicmodeller(topic_modeller, html_documents, tm_data_folder, num_topics):
    topic_modeller.initialize(html_documents, num_topics)
    topic_modeller.save(tm_data_folder)


def initialize_with_existing_dict(topic_modeller, html_documents, tm_data_folder, num_topics):
    topic_modeller.load_dictionary(tm_data_folder)
    topic_modeller.initialize_model(html_documents, num_topics)
    topic_modeller.save_model(tm_data_folder)
