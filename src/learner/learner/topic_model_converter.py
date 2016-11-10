from itertools import chain, izip
import numpy as np


class TopicModelConverter(object):
    """
    Service to convert a feature vector expressed in a origin topic model to the best approximation
    of this vector in a target topic model.
    """

    def __init__(self, origin_model, target_model):
        """
        :param origin_model: struct.TopicModelDescription of the "old" model
        :param target_model: struct.TopicModelDescription of the "new" model
        """
        words = set(topic_word.word
                    for topic in chain(origin_model.topics, target_model.topics)
                    for topic_word in topic.topic_words)  # unique words

        word_to_index = dict(izip(words, range(len(words))))
        origin_model_basis = self._build_basis_matrix(word_to_index, origin_model)
        target_model_basis = self._build_basis_matrix(word_to_index, target_model)
        self._projector = _VectorSpaceProjector(origin_model_basis, target_model_basis)

    @staticmethod
    def _build_basis_matrix(word_to_index, model):
        model_basis = np.zeros((len(word_to_index), len(model.topics)))
        for index_topic, topic in enumerate(model.topics):
            for topic_word in topic.topic_words:
                model_basis[word_to_index[topic_word.word], index_topic] = topic_word.weight
        return model_basis

    def compute_target_vector(self, origin_vector):
        """
        :param origin_vector: classification of element (doc or user profile) in origin_model,
        list of double of size origin_model.nb_topics
        :return: approximation of classification of this element (doc or user profile) in target_model
        list of double of size target_model.nb_topics
        """
        np_origin_vector = np.asarray(origin_vector)
        np_target_vector = self._projector.project_on_target_space(np_origin_vector)
        target_vector = np_target_vector.tolist()
        return target_vector


class _VectorSpaceProjector(object):
    """
    Service to project a vector from a subspace to another inside a common vector space
    """

    def __init__(self, origin_space_basis, target_space_basis):
        """
        :param origin_space_basis: numpy matrix dim_global_space * dim_origin_subspace
        :param target_space_basis: numpy matrix dim_global_space * dim_target_subspace
        -let's call A and B the matrices where each column 'i' is the coordinates of i-th base vector of global subspace
        coordinates, of respectively origin and target subspace.
        -let's call 'a' a vector of coordinates expressed in origin_space referential.
        -We want to find 'b', a vector of coordinates expressed in target_space that is the best approximation of 'a'
        -Best is understood in the sens of the L2 natural norm of the global vector space
        -We search 'b'= arg_min ||Aa-Bb||. By taking Grad[(Aa-Bb).(Aa-Bb)] = 0, we show that:
        This is solved by the linear equation : ( B^T * B ) b = ( B^T * A ) a.
        """
        # pre-compute left hand side (B^T * B) and right hand side ( B^T * A )
        target_space_transposed = target_space_basis.transpose()
        self._left_hand_side = np.dot(target_space_transposed, target_space_basis)
        self._right_hand_side = np.dot(target_space_transposed, origin_space_basis)

    def project_on_target_space(self, vector_in_origin_basis):
        """
        :param vector_in_origin_basis: vector expressed in origin_space_basis
        :return: best projection of input vector on target_space expressed in target_space_basis
        """
        # solve linear equation ( B^T * B ) b = ( B^T * A ) a
        return np.linalg.solve(self._left_hand_side, np.dot(self._right_hand_side, vector_in_origin_basis))
