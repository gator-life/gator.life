import os
from server.dal import Dal
from server.frontendstructs import TopicModelDescription
from topicmodeller.topicmodeller import TopicModeller
from orchestrator.updatemodel import _save_topic_model_and_feature_set


def _init_datastore():
    directory = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(directory, "../..")
    model_dir = os.path.join(root_dir, "docker_images/gator_deps/trained_topic_model")

    topic_modeller = TopicModeller()
    topic_modeller.load(model_dir)

    model_description = TopicModelDescription.make_from_scratch(topic_modeller.get_model_id(), topic_modeller.get_topics())
    _save_topic_model_and_feature_set(Dal(), model_description)

_init_datastore()
