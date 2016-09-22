# -*- coding: utf-8 -*-


class Document(object):  # pylint: disable=too-many-instance-attributes

    @staticmethod
    def make_from_db(url, url_hash, title, summary, datetime, db_key, feature_vector):  # pylint: disable=too-many-arguments
        return Document(url, url_hash, title, summary, datetime, db_key, feature_vector)

    @staticmethod
    def make_from_scratch(url, url_hash, title, summary, feature_vector):
        """
        :param url: string
        :param url_hash: string
        :param title: string
        :param summary: string
        :param feature_vector: frontendstructs.FeatureVector
        :return:
        """
        return Document(
            url, url_hash, title, summary, datetime=None, db_key=None, feature_vector=feature_vector)

    def __init__(self, url, url_hash, title, summary, datetime, db_key, feature_vector):  # pylint: disable=too-many-arguments
        self.url = url
        self.url_hash = url_hash
        self.title = title
        self._db_key = db_key
        self.summary = summary
        self.datetime = datetime
        self.feature_vector = feature_vector


class UserDocument(object):

    @staticmethod
    def make_from_scratch(document, grade):
        return UserDocument(document, grade)

    @staticmethod
    def make_from_db(document, grade):
        return UserDocument(document, grade)

    def __init__(self, document, grade):
        self.document = document
        self.grade = grade


class User(object):

    @staticmethod
    def make_from_db(db_key, email, interests, user_doc_set_db_key, user_computed_profile_db_key):
        return User(db_key, email, interests, user_doc_set_db_key, user_computed_profile_db_key)

    @staticmethod
    def make_from_scratch(email, interests):
        return User(None, email, interests, None, None)

    def __init__(self, db_key, email, interests, user_doc_set_db_key, user_computed_profile_db_key):
        self._db_key = db_key
        self.email = email
        self.interests = interests
        self._user_doc_set_db_key = user_doc_set_db_key
        self._user_computed_profile_db_key = user_computed_profile_db_key


class FeatureVector(object):

    @staticmethod
    def make_from_scratch(vector, feature_set_id):
        return FeatureVector(vector, feature_set_id)

    def __init__(self, vector, feature_set_id):
        self.vector = vector
        self.feature_set_id = feature_set_id

# NB: when we manage dependencies in server, we can reference enum34 and make this class an enum


class UserActionTypeOnDoc(object):
    up_vote = 1
    down_vote = 2
    click_link = 3
    view_link = 4


class UserActionOnDoc(object):

    @staticmethod
    def make_from_scratch(document, action_type):
        return UserActionOnDoc(document, action_type, datetime=None)

    @staticmethod
    def make_from_db(document, action_type, datetime):
        return UserActionOnDoc(document, action_type, datetime)

    def __init__(self, document, action_type, datetime):
        self.document = document
        self.action_type = action_type
        self.datetime = datetime


class UserComputedProfile(object):
    """
    Represent the information about the user profile:
    """
    @staticmethod
    def make_from_scratch(feature_vector, model_data):
        return UserComputedProfile(feature_vector, model_data, datetime=None)

    @staticmethod
    def make_from_db(feature_vector, model_data, datetime):
        return UserComputedProfile(feature_vector, model_data, datetime)

    def __init__(self, feature_vector, model_data, datetime):
        """
        :param feature_vector: FeatureVector, to compute interests of the user for a document in a VSM (Vector Space Model)
        :param model_data: UserProfileModelData, intermediate data to compute this vector at each learning step in profiler
        :param datetime: datetime when the vector has been computed
        """
        self.feature_vector = feature_vector
        self.model_data = model_data
        self.datetime = datetime


class UserProfileModelData(object):

    @staticmethod
    def make_empty(size_vector):
        return UserProfileModelData.make_from_scratch([0] * size_vector, [0] * size_vector, [0] * size_vector, 0.0, 0.0)

    @staticmethod
    def make_from_scratch(explicit_feedback_vector, positive_feedback_vector, negative_feedback_vector,
                          positive_feedback_sum_coeff, negative_feedback_sum_coeff):
        return UserProfileModelData(explicit_feedback_vector, positive_feedback_vector, negative_feedback_vector,
                                    positive_feedback_sum_coeff, negative_feedback_sum_coeff)

    @staticmethod
    def make_from_db(explicit_feedback_vector, positive_feedback_vector, negative_feedback_vector,
                     positive_feedback_sum_coeff, negative_feedback_sum_coeff):
        return UserProfileModelData(explicit_feedback_vector, positive_feedback_vector, negative_feedback_vector,
                                    positive_feedback_sum_coeff, negative_feedback_sum_coeff)

    def __init__(self, explicit_feedback_vector,
                 positive_feedback_vector, negative_feedback_vector,
                 positive_feedback_sum_coeff, negative_feedback_sum_coeff):
        """
        :param explicit_feedback_vector: list, the vector associated to interests of the user
        :param positive_feedback_vector: list, the vector associated to positive actions of the user
        :param negative_feedback_vector: list, the vector associated to negative actions of the user
        :param positive_feedback_sum_coeff: sum of the discounted positive actions of the user
        :param negative_feedback_sum_coeff: sum of the discounted negative actions of the user
        """
        self.explicit_feedback_vector = explicit_feedback_vector
        self.positive_feedback_vector = positive_feedback_vector
        self.negative_feedback_vector = negative_feedback_vector
        self.positive_feedback_sum_coeff = positive_feedback_sum_coeff
        self.negative_feedback_sum_coeff = negative_feedback_sum_coeff
