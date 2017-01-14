import unittest
import numpy as np
from userdocmatch.frontendstructs import TopicModelDescription
from learner.topicmodelapprox import TopicModelConverter, TopicModelApproxClassifier


class TopicModelConverterTests(unittest.TestCase):

    def test_compute_target_vector_with_same_model_return_same_vector(self):
        origin_model = TopicModelDescription.make_from_scratch('orig_id', [
            [('orig_t1_w1', 0.8), ('orig_t1_w2', 0.1)],
            [('orig_t2_w1', 1.0)]
        ])
        target_model = TopicModelDescription.make_from_scratch('target_id', [
            [('orig_t2_w1', 1.0)],
            [('orig_t1_w2', 0.1), ('orig_t1_w1', 0.8)]
        ])
        converter = TopicModelConverter(origin_model, target_model)
        target_vector = converter.compute_target_vector([0.25, 0.75])
        self.assertEquals([0.75, 0.25], target_vector)

    def test_compute_target_vector_with_target_encompass_origin_return_same_vector(self):
        origin_model = TopicModelDescription.make_from_scratch('orig_id', [
            [('orig_t1_w1', 0.8), ('orig_t1_w2', 0.1)],
            [('orig_t2_w1', 1.0)]
        ])
        target_model = TopicModelDescription.make_from_scratch('target_id', [
            [('orig_t2_w1', 1.0)],
            [('orig_t1_w2', 0.1), ('orig_t1_w1', 0.8)],
            [('target_t3_w1', 0.4), ('target_t3_w2', 0.5)]
        ])
        converter = TopicModelConverter(origin_model, target_model)
        target_vector = converter.compute_target_vector([0.25, 0.75])
        self.assertEquals([0.75, 0.25, 0], target_vector)

    def test_compute_target_vector_with_useless_dim_in_origin_return_same_vector(self):
        origin_model = TopicModelDescription.make_from_scratch('orig_id', [
            [('orig_t1_w1', 0.9), ('orig_t1_w2', 0.1)],
            [('orig_t2_w1', 1.0)],
            [('orig_t1_w1', 0.5), ('orig_t3_w2', 0.4)],
        ])
        target_model = TopicModelDescription.make_from_scratch('target_id', [
            [('orig_t2_w1', 1.0)],
            [('orig_t1_w2', 0.1), ('orig_t1_w1', 0.9)]
        ])
        converter = TopicModelConverter(origin_model, target_model)
        target_vector = converter.compute_target_vector([0.25, 0.75, 0])
        self.assertEquals([0.75, 0.25], target_vector)

    def test_compute_target_vector_with_two_topics_merged_return_merged_weights(self):
        origin_model = TopicModelDescription.make_from_scratch('orig_id', [
            [('orig_t1_w1', 0.9), ('orig_t1_w2', 0.1)],
            [('orig_t2_w1', 1.0)]
        ])
        target_model = TopicModelDescription.make_from_scratch('target_id', [
            [('orig_t1_w1', 0.5), ('orig_t2_w1', 0.5)],
            [('orig_t1_w2', 1.0)]
        ])
        converter = TopicModelConverter(origin_model, target_model)
        target_vector = converter.compute_target_vector([0.5, 0.5])
        self.assertEquals([0.95, 0.05], target_vector)

    @staticmethod
    def test_compute_target_vector_with_topic_split_return_split_weights():
        origin_model = TopicModelDescription.make_from_scratch('orig_id', [
            [('orig_t1_w1', 0.5), ('orig_t2_w1', 0.5)],
            [('orig_t1_w2', 1.0)]
        ])
        target_model = TopicModelDescription.make_from_scratch('target_id', [
            [('orig_t1_w1', 0.9), ('orig_t1_w2', 0.1)],
            [('orig_t2_w1', 1.0)]
        ])
        converter = TopicModelConverter(origin_model, target_model)
        target_vector = converter.compute_target_vector([1.0, 0.0])
        np.testing.assert_almost_equal([0.55, 0.5], target_vector, 3)

    def test_compute_target_vector_with_no_shared_word_from_used_topic_return_zero(self):
        origin_model = TopicModelDescription.make_from_scratch('orig_id', [
            [('orig_t1_w1', 0.5), ('orig_t2_w1', 0.5)],
            [('orig_t1_w2', 1.0)]
        ])
        target_model = TopicModelDescription.make_from_scratch('target_id', [
            [('target_t1_w1', 0.9), ('target_t1_w2', 0.1)],
            [('orig_t1_w2', 1.0)]
        ])
        converter = TopicModelConverter(origin_model, target_model)
        target_vector = converter.compute_target_vector([1.0, 0.0])
        self.assertEquals([0, 0], target_vector)

    def test_compute_target_vector_with_no_shared_word_between_models_return_zero(self):
        origin_model = TopicModelDescription.make_from_scratch('orig_id', [
            [('orig_t1_w1', 0.5), ('orig_t2_w1', 0.5)],
            [('orig_t1_w2', 1.0)]
        ])
        target_model = TopicModelDescription.make_from_scratch('target_id', [
            [('target_t1_w1', 0.9), ('target_t1_w2', 0.1)],
            [('target_t2_w1', 1.0)]
        ])
        converter = TopicModelConverter(origin_model, target_model)
        target_vector = converter.compute_target_vector([0.5, 0.5])
        self.assertEquals([0, 0], target_vector)


class TopicModelApproxClassifierTest(unittest.TestCase):

    def test_compute_classified_vector_no_shared_word_return_zero(self):
        model = TopicModelDescription.make_from_scratch('id', [
            [('t1_w1', 0.5), ('t1_w2', 0.5)],
            [('t2_w1', 1.0)]
        ])
        classifier = TopicModelApproxClassifier(model)
        classified = classifier.compute_classified_vector(['w3'])
        self.assertEquals([0, 0], classified)

    @staticmethod
    def test_compute_classified_vector_shared_word_on_one_topic():
        model = TopicModelDescription.make_from_scratch('id', [
            [('t1_w1', 0.5), ('t1_w2', 0.5)],
            [('t2_w1', 1.0)]
        ])
        classifier = TopicModelApproxClassifier(model)
        classified = classifier.compute_classified_vector(['t1_w1', 'w3'])
        np.testing.assert_almost_equal([1.0, 0], classified, 10)

    @staticmethod
    def test_compute_classified_vector_shared_word_on_two_topics_return_biggest_weight():
        model = TopicModelDescription.make_from_scratch('id', [
            [('t1_w1', 0.5), ('t1_w2', 0.5)],
            [('t1_w1', 1.0)]
        ])
        classifier = TopicModelApproxClassifier(model)
        classified = classifier.compute_classified_vector(['t1_w1'])
        np.testing.assert_almost_equal([0.0, 1.0], classified, 10)

    @staticmethod
    def test_compute_classified_vector_words_on_two_topics_split():
        model = TopicModelDescription.make_from_scratch('id', [
            [('t1_w1', 0.5), ('t1_w2', 0.5)],
            [('t2_w1', 1.0)]
        ])
        classifier = TopicModelApproxClassifier(model)
        classified = classifier.compute_classified_vector(['t1_w1', 't2_w1'])
        np.testing.assert_almost_equal([1.0, 1.0], classified, 10)

if __name__ == '__main__':
    unittest.main()
