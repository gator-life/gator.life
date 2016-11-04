# -*- coding: utf-8 -*-
"""
DAL (Data Access Layer) module
abstract database scheme and datastore API to communicate with the rest of the packages
through objects uncoupled from gcloud datastore API
"""
import datetime
import httplib2
from gcloud import datastore
from .environment import GCLOUD_PROJECT, IS_TEST_ENV
from . import frontendstructs as struct

REF_FEATURE_SET = u"ref_feature_set"
NULL_FEATURE_SET = u"null_feature_set"


def _to_user_action_type_on_doc(user_action_on_doc_db_string):
    if user_action_on_doc_db_string == 'up_vote':
        return struct.UserActionTypeOnDoc.up_vote
    if user_action_on_doc_db_string == 'down_vote':
        return struct.UserActionTypeOnDoc.down_vote
    if user_action_on_doc_db_string == 'click_link':
        return struct.UserActionTypeOnDoc.click_link
    if user_action_on_doc_db_string == 'view_link':
        return struct.UserActionTypeOnDoc.view_link
    raise ValueError(user_action_on_doc_db_string + ' has no matching for Enum UserActionTypeOnDoc')
# NB: when struct.UserActionTypeOnDoc become an Enum, we can just call user_action_on_doc_enum.name


def _to_db_action_type_on_doc(user_action_on_doc_enum):
    if user_action_on_doc_enum == struct.UserActionTypeOnDoc.up_vote:
        return 'up_vote'
    if user_action_on_doc_enum == struct.UserActionTypeOnDoc.down_vote:
        return 'down_vote'
    if user_action_on_doc_enum == struct.UserActionTypeOnDoc.click_link:
        return 'click_link'
    if user_action_on_doc_enum == struct.UserActionTypeOnDoc.view_link:
        return 'view_link'
    raise ValueError(str(user_action_on_doc_enum) + ' has not string matching for database')


def _to_user_profile_model_data(db_user_profile_model_data):
    return struct.UserProfileModelData.make_from_db(
        db_user_profile_model_data.get('explicit_feedback_vector', []),
        db_user_profile_model_data.get('positive_feedback_vector', []),
        db_user_profile_model_data.get('negative_feedback_vector', []),
        db_user_profile_model_data['positive_feedback_sum_coeff'],
        db_user_profile_model_data['negative_feedback_sum_coeff']
    )


def _to_user(db_user):
    return struct.User.make_from_db(
        db_key=db_user.key,
        email=db_user['email'],
        interests=db_user.get('interests', []),
        user_doc_set_db_key=db_user['user_doc_set_key'],
        user_computed_profile_db_key=db_user['user_computed_profile_key'])


def _to_user_password(db_user):
    return db_user['password']


def _to_user_doc(doc, db_user_doc):
    return struct.UserDocument.make_from_scratch(document=doc, grade=db_user_doc['grade'])


def _to_user_action_on_doc(doc, db_user_action_on_doc):
    action_type = _to_user_action_type_on_doc(db_user_action_on_doc['action_type'])
    return struct.UserActionOnDoc.make_from_db(doc, action_type, db_user_action_on_doc['datetime'])


def _to_feature_vector(db_feature_vector):
    vector = db_feature_vector.get('vector', [])
    feature_set_id = db_feature_vector['feature_set_key'].name
    return struct.FeatureVector.make_from_scratch(vector=vector, feature_set_id=feature_set_id)


def _to_user_computed_profile(db_user_computed_profile):
    model_data = _to_user_profile_model_data(db_user_computed_profile['model_data'])
    feature_vector = _to_feature_vector(db_user_computed_profile['feature_vector'])
    update_datetime = db_user_computed_profile['datetime']
    return struct.UserComputedProfile.make_from_db(feature_vector, model_data, update_datetime)


def _to_doc(db_doc):
    return struct.Document.make_from_db(
        url=db_doc['url'], url_hash=db_doc.key.name, title=db_doc['title'], summary=db_doc['summary'],
        datetime=db_doc['datetime'], feature_vector=_to_feature_vector(db_doc['feature_vector']))


def _datastore_client():

    class _EmulatorCreds(object):
        """
        mock of credentials for local datastore
        cf. https://github.com/GoogleCloudPlatform/gcloud-python/issues/1839
        """
        @staticmethod
        def create_scoped_required():
            return False

    if IS_TEST_ENV:
        credentials = _EmulatorCreds()
        http = httplib2.Http()  # Un-authorized.
        return datastore.Client(project=GCLOUD_PROJECT, credentials=credentials, http=http)
    else:
        return datastore.Client(GCLOUD_PROJECT)


class DatastoreHelper(object):

    def __init__(self, datastore_client):
        self._ds_client = datastore_client

    def make_entity(self, entity_type, not_indexed):
        key = self._ds_client.key(entity_type)
        return datastore.entity.Entity(key, exclude_from_indexes=not_indexed)

    def make_named_entity(self, entity_type, key_name, not_indexed):
        key = self._ds_client.key(entity_type, key_name)
        return datastore.entity.Entity(key, exclude_from_indexes=not_indexed)

    def get_multi(self, keys):
        """
        Wrapper around get_multi datastore function that ensure matching of indexes between keys and retrieved entities.
        It seems to works natively at least with test gcloud server but it's not clearly specified.
        :param keys: list of gcloud.datastore.entity.key
        :return: list of gcloud.datastore.entity
        """
        entities = self._ds_client.get_multi(keys)
        key_to_entity = dict((entity.key, entity) for entity in entities)
        return [key_to_entity[key] for key in keys]


class Dal(object):  # pylint: disable= too-many-instance-attributes
    # Dal is a class rather than plain module functions to enable init logic in the future,
    # but datastore client is slow to initialize, so we share it between Dal instances

    _ds_client = _datastore_client()

    def __init__(self):
        ds_helper = DatastoreHelper(self._ds_client)
        self.feature_set = DalFeatureSet(self._ds_client, ds_helper)
        self.feature_vector = DalFeatureVector(self._ds_client, ds_helper)
        self.doc = DalDoc(self._ds_client, ds_helper, self.feature_vector)
        self.user_action = DalUserActionOnDoc(self._ds_client, ds_helper, self.doc)
        self.user_computed_profile = DalUserComputedProfile(self._ds_client, ds_helper, self.feature_vector)
        self.user = DalUser(self._ds_client, ds_helper, self.user_computed_profile)
        self.user_doc = DalUserDoc(self._ds_client, ds_helper, self.doc)
        self.topic_model = DalTopicModelDescription(self._ds_client, ds_helper)


class DalFeatureSet(object):

    def __init__(self, datastore_client, datastore_helper):
        self._ds_client = datastore_client
        self._helper = datastore_helper

    def get_feature_set(self, feature_set_id):
        """
        :param feature_set_id: string
        :return: struct.FeatureSet
        """
        db_feature_set_key = self._ds_client.key(u'FeatureSet', feature_set_id)
        db_feature_set = self._ds_client.get(db_feature_set_key)
        feature_names = db_feature_set.get('features', [])
        model_id = db_feature_set['model_id']
        return struct.FeatureSet.make_from_db(feature_set_id, feature_names, model_id)

    def save_feature_set(self, feature_set):
        """
        :param feature_set: struct.FeatureSet
        """
        db_feature_set = self._helper.make_named_entity(u'FeatureSet', feature_set.feature_set_id, not_indexed=('features',))
        db_feature_set['features'] = feature_set.feature_names
        db_feature_set['model_id'] = feature_set.model_id
        self._ds_client.put(db_feature_set)


class DalFeatureVector(object):

    def __init__(self, datastore_client, datastore_helper):
        self._ds_client = datastore_client
        self._helper = datastore_helper

    def _to_db_feature_vector(self, feature_vector):
        db_feature_vector = self._helper.make_entity(u'FeatureVector', not_indexed=('vector',))
        db_feature_vector['feature_set_key'] = self._ds_client.key(u'FeatureSet', feature_vector.feature_set_id)
        db_feature_vector['vector'] = feature_vector.vector
        return db_feature_vector


class DalDoc(object):

    def __init__(self, datastore_client, datastore_helper, dal_feature_vector):
        self._ds_client = datastore_client
        self._helper = datastore_helper
        self._dal_feature_vector = dal_feature_vector

    def save_documents(self, documents):
        """
        :param documents: list of struct.Document
        """
        docs_with_order = [doc for doc in documents]
        db_docs = [self._to_db_doc(doc) for doc in docs_with_order]
        self._ds_client.put_multi(db_docs)
        db_doc_keys = [db_doc.key for db_doc in db_docs]
        for (doc, key) in zip(docs_with_order, db_doc_keys):
            doc._db_key = key  # pylint: disable=protected-access

    def _to_db_doc(self, doc):
        not_indexed = ('title', 'summary', 'feature_vector')
        db_doc = self._helper.make_named_entity('Document', doc.url_hash, not_indexed)
        db_doc['url'] = doc.url
        db_doc['title'] = doc.title
        db_doc['summary'] = doc.summary
        db_doc['feature_vector'] = self._dal_feature_vector._to_db_feature_vector(  # pylint: disable=protected-access
            doc.feature_vector)
        db_doc['datetime'] = doc.datetime or datetime.datetime.utcnow()
        return db_doc

    def get_doc(self, url_hash):
        """
        :param url_hash: string corresponding to the field 'url_hash' of a struct.Document
        :return: struct.Document
        """
        return self.get_docs([url_hash])[0]

    def get_docs(self, url_hashes):
        """
        :param url_hashes: list of string corresponding to the field 'url_hash' of a struct.Document
        :return: list of struct.Document matching url_hashes list
        """
        db_keys = [self._ds_client.key('Document', url_hash) for url_hash in url_hashes]
        db_docs = self._helper.get_multi(db_keys)
        return [_to_doc(db_doc) for db_doc in db_docs]

    def get_recent_doc_url_hashes(self, from_datetime):
        """
        :param from_datetime: datetime
        :return: the list of hashes of docs whose datetime is after from_datetime
        """
        query = self._ds_client.query(kind='Document')
        query.keys_only()
        query.add_filter('datetime', '>', from_datetime)
        db_doc_entities = query.fetch()
        return [entity.key.name for entity in db_doc_entities]


class DalUserActionOnDoc(object):

    def __init__(self, datastore_client, datastore_helper, dal_doc):
        self._ds_client = datastore_client
        self._helper = datastore_helper
        self._dal_doc = dal_doc

    def save_user_action_on_doc(self, user, document, action_on_doc):
        """
        :param user: frontendstructs.User
        :param document: frontendstructs.Document
        :param action_on_doc: frontendstructs.UserActionTypeOnDoc
        """
        db_action = self._to_db_user_action_on_doc(user, document, action_on_doc)
        self._ds_client.put(db_action)

    def _to_db_user_action_on_doc(self, user, document, action_on_doc):
        db_action = self._helper.make_entity('UserActionOnDoc', not_indexed=())
        db_action['user_key'] = user._db_key  # pylint: disable=protected-access
        db_action['document_url_hash'] = document.url_hash
        db_action['action_type'] = _to_db_action_type_on_doc(action_on_doc)
        db_action['datetime'] = datetime.datetime.utcnow()
        return db_action

    def get_user_actions_on_docs(self, users, from_datetime):
        """
        :param users: list of frontendstructs.User
        :param from_datetime:
        :return: return a list matching users input list, each element is the list of frontendstructs.UserActionOnDoc
         for this user inserted after 'from_datetime'
        """
        # 1) retrieve actions from database
        actions_query = self._ds_client.query(kind='UserActionOnDoc')
        actions_query.add_filter('datetime', '>', from_datetime)
        db_actions = list(actions_query.fetch())
        # NB: we only filter on datetime (and not the users) on the query because you can't mix
        # an 'IN something' query with other filter in datastore.
        # Moreover, request with filter 'IN users' is limited to 30 elements and is very inefficient
        # a long term solution if we need scalability is to replace users list by a range (min_user, max_user).
        # fetch(10000) is not scalable either, but I won't make something complex because I think
        # this second point would be solved if the first one (filter on user range) is solved

        # 2) retrieve docs present in actions from database
        doc_url_hashes = list(set(action['document_url_hash'] for action in db_actions))

        docs = self._dal_doc.get_docs(doc_url_hashes)  # pylint: disable=protected-access
        doc_hash_to_doc = dict(zip(doc_url_hashes, docs))

        # 3) build result, from two above database results
        actions_by_user = [[] for _ in users]
        user_mail_to_index = dict(zip((user.email for user in users), range(len(users))))
        for db_action in db_actions:
            doc = doc_hash_to_doc[db_action['document_url_hash']]
            action = _to_user_action_on_doc(doc, db_action)
            user_index = user_mail_to_index.get(db_action['user_key'].name)
            if user_index is not None:  # because we did not filter query on users
                actions_by_user[user_index].append(action)
        return actions_by_user


class DalUserComputedProfile(object):

    def __init__(self, datastore_client, datastore_helper, dal_feature_vector):
        self._ds_client = datastore_client
        self._helper = datastore_helper
        self._dal_feature_vector = dal_feature_vector

    def _to_db_user_profile_model_data(self, user_profile_model_data):
        not_indexed = ('explicit_feedback_vector', 'positive_feedback_vector', 'negative_feedback_vector',
                       'positive_feedback_sum_coeff', 'negative_feedback_sum_coeff')
        db_user_profile_model_data = self._helper.make_entity(u'UserProfileModelData', not_indexed)
        db_user_profile_model_data['explicit_feedback_vector'] = user_profile_model_data.explicit_feedback_vector
        db_user_profile_model_data['positive_feedback_vector'] = user_profile_model_data.positive_feedback_vector
        db_user_profile_model_data['negative_feedback_vector'] = user_profile_model_data.negative_feedback_vector
        db_user_profile_model_data['positive_feedback_sum_coeff'] = user_profile_model_data.positive_feedback_sum_coeff
        db_user_profile_model_data['negative_feedback_sum_coeff'] = user_profile_model_data.negative_feedback_sum_coeff

        return db_user_profile_model_data

    def _to_db_user_computed_profile(self, user_computed_profile):
        not_indexed = ('feature_vector', 'model_data', 'datetime')
        db_user_computed_profile = self._helper.make_entity(u'UserComputedProfile', not_indexed)
        db_user_computed_profile['feature_vector'] =\
            self._dal_feature_vector._to_db_feature_vector(  # pylint: disable=protected-access
                user_computed_profile.feature_vector)
        db_user_computed_profile['model_data'] = self._to_db_user_profile_model_data(user_computed_profile.model_data)
        db_user_computed_profile['datetime'] = user_computed_profile.datetime or datetime.datetime.utcnow()
        return db_user_computed_profile

    def save_user_computed_profile(self, user, user_computed_profile):
        self.save_user_computed_profiles([(user, user_computed_profile)])

    def save_user_computed_profiles(self, user_profile_list):
        """
        :param user_profile_list: list of tuples (struct.User, struct.UserComputedProfile)
        """
        db_profiles = []
        for user, user_computed_profile in user_profile_list:
            db_profile = self._to_db_user_computed_profile(user_computed_profile)
            # by setting as key the key previously referenced by the user, we will overwrite the previous profile in db
            db_profile.key = user._user_computed_profile_db_key  # pylint: disable=protected-access
            db_profiles.append(db_profile)
        self._ds_client.put_multi(db_profiles)

    def get_user_computed_profiles(self, users):
        """
        :param users: list of Struct.User
        :return: list of struct.UserComputedProfile matching 'users' list
        """
        keys = [user._user_computed_profile_db_key for user in users]  # pylint: disable=protected-access
        db_profiles = self._helper.get_multi(keys)
        profiles = [_to_user_computed_profile(db_profile) for db_profile in db_profiles]
        return profiles

    def get_user_feature_vector(self, user):
        """
        :param user: struct.User
        :return: struct.FeatureVector
        """
        return self.get_users_feature_vectors([user])[0]

    def get_users_feature_vectors(self, users):
        """
        :param users: list of struct.User
        :return: list of struct.FeatureVector matching 'users' list
        """
        # NB: this could be probably optimized by projection query if we need, but it would require to index vector property.
        profiles = self.get_user_computed_profiles(users)
        return [profile.feature_vector for profile in profiles]


class DalUserDoc(object):

    def __init__(self, datastore_client, datastore_helper, dal_doc):
        self._ds_client = datastore_client
        self._helper = datastore_helper
        self._dal_doc = dal_doc

    def _to_user_docs(self, db_user_doc_set):
        if 'user_documents' not in db_user_doc_set:  # cannot save an empty list in datastore: field would be removed
            return []
        db_user_docs = db_user_doc_set['user_documents']
        doc_url_hashes = [user_doc['document_url_hash'] for user_doc in db_user_docs]
        docs = self._dal_doc.get_docs(doc_url_hashes)
        user_docs = [_to_user_doc(doc, db_user_doc) for doc, db_user_doc in zip(docs, db_user_docs)]
        return user_docs

    def save_user_docs(self, user, user_docs):
        """
        :param user: struct.user
        :param user_docs: list of struct.UserDocument
        :return:
        """
        user_doc_set_db_key = user._user_doc_set_db_key  # pylint: disable=protected-access
        db_user_doc_set = self._ds_client.get(user_doc_set_db_key)
        db_user_docs = self._to_db_user_docs(user_docs)
        db_user_doc_set['user_documents'] = db_user_docs
        self._ds_client.put(db_user_doc_set)

    def _to_db_user_docs(self, user_docs):
        db_user_docs = [self._to_db_user_doc(user_doc) for user_doc in user_docs]
        return db_user_docs

    def _to_db_user_doc(self, user_doc):
        db_user_doc = self._helper.make_entity(u'UserDocument', not_indexed=())
        db_user_doc['document_url_hash'] = user_doc.document.url_hash
        db_user_doc['grade'] = user_doc.grade
        return db_user_doc

    def save_users_docs(self, user_to_user_docs_list):
        """
        Save UserDocuments list associated to each User
        :param user_to_user_docs_list: list of tuples (User, List of UserDocument)
        """
        user_set_db_keys = []
        users_docs = []
        for user, user_docs in user_to_user_docs_list:
            user_set_db_keys.append(user._user_doc_set_db_key)  # pylint: disable=protected-access
            users_docs.append(user_docs)
        db_user_sets = self._helper.get_multi(user_set_db_keys)
        for (db_user_set, user_docs) in zip(db_user_sets, users_docs):
            db_user_set['user_documents'] = self._to_db_user_docs(user_docs)
        self._ds_client.put_multi(db_user_sets)

    def get_user_docs(self, user):
        """
        :param user: struct.User
        :return: list of struct.UserDocument
        """
        user_doc_set = self._ds_client.get(user._user_doc_set_db_key)  # pylint: disable=protected-access
        return self._to_user_docs(user_doc_set)

    def get_users_docs(self, users):
        """
        :param users: list of struct.User
        :return: list matching 'users' list, each list being a list of struct.UserDocument
        """
        def to_user_doc(db_user_doc):
            return _to_user_doc(hashes_to_docs[db_user_doc['document_url_hash']], db_user_doc)

        def db_set_to_user_doc_list(db_user_doc_set):
            db_user_docs = db_docs(db_user_doc_set)
            return [to_user_doc(db_user_doc) for db_user_doc in db_user_docs]

        def db_docs(db_user_doc_set):
            return db_user_doc_set.get('user_documents', [])

        user_doc_set_db_keys = [user._user_doc_set_db_key for user in users]  # pylint: disable=protected-access
        db_user_doc_sets = self._helper.get_multi(user_doc_set_db_keys)
        doc_hashes_set = {user_doc['document_url_hash']
                          for user_doc_set in db_user_doc_sets for user_doc in db_docs(user_doc_set)}
        doc_hashes_list = list(doc_hashes_set)
        docs = self._dal_doc.get_docs(doc_hashes_list)
        hashes_to_docs = dict(zip(doc_hashes_list, docs))

        return [db_set_to_user_doc_list(db_user_doc_set) for db_user_doc_set in db_user_doc_sets]


class DalUser(object):

    def __init__(self, datastore_client, datastore_helper, dal_user_computed_profile):
        self._ds_client = datastore_client
        self._helper = datastore_helper
        self._dal_user_computed_profile = dal_user_computed_profile

    def get_user(self, email):
        """
        :param email:
        :return: Struct.User if user found, else None
        """
        (user, _) = self.get_user_and_password(email)
        return user

    def get_user_and_password(self, email):
        """
        :param email:
        :return: A tuple (Struct.User, encoded password) if user found, else (None, None)
        """
        key = self._ds_client.key('User', email)
        db_user = self._ds_client.get(key)
        return (_to_user(db_user), _to_user_password(db_user)) if db_user else (None, None)

    def get_all_users(self):
        """
        :return: A list of struct.User of all users in database
        """
        all_users_query = self._ds_client.query(kind='User').fetch()
        return [_to_user(db_user) for db_user in all_users_query]

    def save_user(self, user, password):
        """
        save a user into the database, if it's newly created, db_keys will be initialized
        """
        if user._user_doc_set_db_key is None:  # pylint: disable=protected-access
            user_doc_set_db = self._helper.make_entity('UserDocumentSet', not_indexed=('user_documents',))
            user_doc_set_db['user_documents'] = []
            self._ds_client.put(user_doc_set_db)
            user._user_doc_set_db_key = user_doc_set_db.key  # pylint: disable=protected-access
        if user._user_computed_profile_db_key is None:  # pylint: disable=protected-access

            user_computed_profile = struct.UserComputedProfile.make_from_scratch(
                struct.FeatureVector.make_from_scratch([], NULL_FEATURE_SET),
                struct.UserProfileModelData.make_from_scratch([], [], [], 0.0, 0.0))
            db_user_computed_profile = \
                self._dal_user_computed_profile._to_db_user_computed_profile(  # pylint: disable=protected-access
                    user_computed_profile)
            self._ds_client.put(db_user_computed_profile)
            user._user_computed_profile_db_key = db_user_computed_profile.key  # pylint: disable=protected-access

        db_user = self._to_db_user(user, password)
        self._ds_client.put(db_user)
        user._db_key = db_user.key  # pylint: disable=protected-access

    def _to_db_user(self, user, password):
        not_indexed = ('password', 'interests', 'user_doc_set_key', 'user_computed_profile_key')
        db_user = self._helper.make_named_entity('User', user.email, not_indexed)
        db_user['email'] = user.email
        db_user['password'] = password
        db_user['interests'] = user.interests
        db_user['user_doc_set_key'] = user._user_doc_set_db_key  # pylint: disable=protected-access
        db_user['user_computed_profile_key'] = user._user_computed_profile_db_key  # pylint: disable=protected-access
        return db_user


class DalTopicModelDescription(object):

    def __init__(self, datastore_client, datastore_helper):
        self._ds_client = datastore_client
        self._helper = datastore_helper

    def get(self, model_id):
        """
        :param model_id: string, model unique identifier
        :return: struct.TopicModelDescription
        """
        key = self._ds_client.key(u'TopicModelDescription', model_id)
        db_model = self._ds_client.get(key)
        db_topics = db_model['topics']
        topics = [zip(db_topic['words'], db_topic['weights']) for db_topic in db_topics]
        return struct.TopicModelDescription.make_from_scratch(model_id, topics)

    def save(self, model_description):
        """
        :param model_description: struct.TopicModelDescription
        """
        not_indexed = ['topics']
        db_model = self._helper.make_named_entity(u'TopicModelDescription', model_description.topic_model_id, not_indexed)
        db_model['topics'] = [self._to_db_topic(topic) for topic in model_description.topics]
        self._ds_client.put(db_model)

    def _to_db_topic(self, topic):
        not_indexed = ['words', 'weights']
        db_topic = self._helper.make_entity(u'Topic', not_indexed)
        db_topic['words'] = [topic_word.word for topic_word in topic.topic_words]
        db_topic['weights'] = [topic_word.weight for topic_word in topic.topic_words]
        return db_topic
