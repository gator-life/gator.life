"""
DAL (Data Access Layer) module
abstract database scheme and datastore API to communicate with the rest of the package through pure (not ndb) Python objects
"""
import datetime
import httplib2
import jsonpickle
from gcloud import datastore
from environment import GCLOUD_PROJECT, IS_TEST_ENV   # pylint: disable=relative-import
import frontendstructs as struct   # pylint: disable=relative-import


REF_FEATURE_SET = u"ref_feature_set"
NULL_FEATURE_SET = u"null_feature_set"


def _to_urlsafe(key):
    """
    Encode a key to a string that can be passed as an url parameter
    Be careful, this is only encoded, not encrypted.
    """
    # encode call transform key to a string, then b64encode to a base64 format that can be passed in an url
    return jsonpickle.util.b64encode(jsonpickle.encode(key))


def _to_key(urlsafe):
    """
    Decode back to a key than has been encoded with _to_urlsafe(key)
    """
    return jsonpickle.decode(jsonpickle.util.b64decode(urlsafe))


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
        user_doc_set_db_key=db_user['user_document_set_key'],
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
        url=db_doc['url'], title=db_doc['title'], summary=db_doc['summary'], datetime=db_doc['datetime'],
        db_key=db_doc.key, key_urlsafe=_to_urlsafe(db_doc.key),
        feature_vector=_to_feature_vector(db_doc['feature_vector']))


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


class Dal(object):
    # Dal is a class rather than plain module functions to enable init logic in the future,
    # but datastore client is slow to initialize, so we share it between Dal instances
    _ds_client = _datastore_client()

    def _make_entity(self, entity_type, not_indexed):
        key = self._ds_client.key(entity_type)
        return datastore.entity.Entity(key, exclude_from_indexes=not_indexed)

    def _make_named_entity(self, entity_type, key_name, not_indexed):
        key = self._ds_client.key(entity_type, key_name)
        return datastore.entity.Entity(key, exclude_from_indexes=not_indexed)

    def get_user(self, email):
        (user, _) = self.get_user_and_password(email)
        return user

    def get_user_and_password(self, email):
        """
        :param email:
        :return: A tuple (Struct.User, encoded password)
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
            user_doc_set_db = self._make_entity('UserDocumentSet', not_indexed=('user_documents',))
            user_doc_set_db['user_documents'] = []
            self._ds_client.put(user_doc_set_db)
            user._user_doc_set_db_key = user_doc_set_db.key  # pylint: disable=protected-access
        if user._user_computed_profile_db_key is None:  # pylint: disable=protected-access

            user_computed_profile = struct.UserComputedProfile.make_from_scratch(
                struct.FeatureVector.make_from_scratch([], NULL_FEATURE_SET),
                struct.UserProfileModelData.make_from_scratch([], [], 0.0, 0.0))
            db_user_computed_profile = self._to_db_computed_user_profile(user_computed_profile)
            self._ds_client.put(db_user_computed_profile)
            user._user_computed_profile_db_key = db_user_computed_profile.key  # pylint: disable=protected-access

        db_user = self._to_db_user(user, password)
        self._ds_client.put(db_user)
        user._db_key = db_user.key  # pylint: disable=protected-access

    def _to_db_user(self, user, password):
        not_indexed = ('password', 'interests', 'user_document_set_key', 'user_computed_profile_key')
        db_user = self._make_named_entity('User', user.email, not_indexed)
        db_user['email'] = user.email
        db_user['password'] = password
        db_user['interests'] = user.interests
        db_user['user_document_set_key'] = user._user_doc_set_db_key  # pylint: disable=protected-access
        db_user['user_computed_profile_key'] = user._user_computed_profile_db_key  # pylint: disable=protected-access
        return db_user

    def get_features(self, feature_set_id):
        """
        :param feature_set_id: string
        :return: a list of string of feature labels of the feature_set_id. This list matches the order of the elements
        in the feature vectors associated to this feature_set_id.
        """
        db_feature_set_key = self._ds_client.key(u'FeatureSet', feature_set_id)
        db_feature_set = self._ds_client.get(db_feature_set_key)
        return db_feature_set.get('features', [])

    def save_features(self, feature_set_id, feature_names):
        db_feature_set = self._make_named_entity(u'FeatureSet', feature_set_id, not_indexed=('features',))
        db_feature_set['features'] = feature_names
        self._ds_client.put(db_feature_set)

    def _to_db_user_profile_model_data(self, user_profile_model_data):
        not_indexed = ('positive_feedback_vector', 'negative_feedback_vector',
                       'positive_feedback_sum_coeff', 'negative_feedback_sum_coeff')
        db_user_profile_model_data = self._make_entity(u'UserProfileModelData', not_indexed)
        db_user_profile_model_data['positive_feedback_vector'] = user_profile_model_data.positive_feedback_vector
        db_user_profile_model_data['negative_feedback_vector'] = user_profile_model_data.negative_feedback_vector
        db_user_profile_model_data['positive_feedback_sum_coeff'] = user_profile_model_data.positive_feedback_sum_coeff
        db_user_profile_model_data['negative_feedback_sum_coeff'] = user_profile_model_data.negative_feedback_sum_coeff

        return db_user_profile_model_data

    def _to_db_computed_user_profile(self, user_computed_profile):
        not_indexed = ('feature_vector', 'model_data', 'datetime')
        db_computed_user_profile = self._make_entity(u'UserComputedProfile', not_indexed)
        db_computed_user_profile['feature_vector'] = self._to_db_feature_vector(user_computed_profile.feature_vector)
        db_computed_user_profile['model_data'] = self._to_db_user_profile_model_data(user_computed_profile.model_data)
        db_computed_user_profile['datetime'] = datetime.datetime.utcnow()
        return db_computed_user_profile

    def _to_db_feature_vector(self, feature_vector):
        db_feature_vector = self._make_entity(u'FeatureVector', not_indexed=('vector',))
        db_feature_vector['feature_set_key'] = self._ds_client.key(u'FeatureSet', feature_vector.feature_set_id)
        db_feature_vector['vector'] = feature_vector.vector
        return db_feature_vector

    def save_computed_user_profile(self, user, user_computed_profile):
        self.save_computed_user_profiles([(user, user_computed_profile)])

    def save_computed_user_profiles(self, user_profile_list):
        """
        :param user_profile_list: list of tuples (struct.User, struct.UserComputedProfile)
        :return:
        """
        db_profiles = []
        for user, computed_user_profile in user_profile_list:
            db_profile = self._to_db_computed_user_profile(computed_user_profile)
            # by setting as key the key previously referenced by the user, we will overwrite the previous profile in db
            db_profile.key = user._user_computed_profile_db_key  # pylint: disable=protected-access
            db_profiles.append(db_profile)
        self._ds_client.put_multi(db_profiles)

    def get_user_computed_profiles(self, users):
        keys = [user._user_computed_profile_db_key for user in users]  # pylint: disable=protected-access
        db_profiles = self._ds_client.get_multi(keys)
        profiles = [_to_user_computed_profile(db_profile) for db_profile in db_profiles]
        return profiles

    def get_user_feature_vector(self, user):
        return self.get_users_feature_vectors([user])[0]

    def get_users_feature_vectors(self, users):
        # NB: this could be probably optimized by projection query if we need, but it would require to index vector property.
        profiles = self.get_user_computed_profiles(users)
        return [profile.feature_vector for profile in profiles]

    def _to_user_docs(self, db_user_doc_set):
        if 'user_documents' not in db_user_doc_set:  # cannot save an empty list in datastore: field would be removed
            return []
        db_user_docs = db_user_doc_set['user_documents']
        db_doc_keys = [user_doc['document_key'] for user_doc in db_user_docs]
        docs = self._to_docs(db_doc_keys)
        user_docs = [_to_user_doc(doc, db_user_doc) for doc, db_user_doc in zip(docs, db_user_docs)]
        return user_docs

    def _to_docs(self, db_doc_keys):
        db_docs = self._ds_client.get_multi(db_doc_keys)
        docs = [_to_doc(db_doc) for db_doc in db_docs]
        return docs

    def save_user_docs(self, user, user_docs):
        user_doc_set_db_key = user._user_doc_set_db_key  # pylint: disable=protected-access
        db_user_doc_set = self._ds_client.get(user_doc_set_db_key)
        db_user_docs = self._to_db_user_docs(user_docs)
        db_user_doc_set['user_documents'] = db_user_docs
        self._ds_client.put(db_user_doc_set)

    def _to_db_user_docs(self, user_docs):
        db_user_docs = [self._to_db_user_doc(user_doc) for user_doc in user_docs]
        return db_user_docs

    def _to_db_user_doc(self, user_doc):
        db_user_doc = self._make_entity(u'UserDocument', not_indexed=())
        db_user_doc['document_key'] = user_doc.document._db_key  # pylint: disable=protected-access
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
        db_user_sets = self._ds_client.get_multi(user_set_db_keys)
        for (db_user_set, user_docs) in zip(db_user_sets, users_docs):  # zip is ok because ndb.get_multi() maintains order
            db_user_set['user_documents'] = self._to_db_user_docs(user_docs)
        self._ds_client.put_multi(db_user_sets)

    def get_user_docs(self, user):
        user_doc_set = self._ds_client.get(user._user_doc_set_db_key)  # pylint: disable=protected-access
        return self._to_user_docs(user_doc_set)

    def get_users_docs(self, users):
        def to_user_doc(db_user_doc):
            return _to_user_doc(keys_to_docs[db_user_doc['document_key']], db_user_doc)

        def db_set_to_user_doc_list(db_user_doc_set):
            db_user_docs = db_docs(db_user_doc_set)
            return [to_user_doc(db_user_doc) for db_user_doc in db_user_docs]

        def db_docs(db_user_doc_set):
            return db_user_doc_set.get('user_documents', [])

        user_doc_set_db_keys = [user._user_doc_set_db_key for user in users]  # pylint: disable=protected-access
        db_user_doc_sets = self._ds_client.get_multi(user_doc_set_db_keys)
        doc_keys_set = {user_doc['document_key'] for user_doc_set in db_user_doc_sets for user_doc in db_docs(user_doc_set)}
        doc_keys_list = list(doc_keys_set)
        docs = self._to_docs(doc_keys_list)
        keys_to_docs = dict(zip(doc_keys_list, docs))

        return [db_set_to_user_doc_list(db_user_doc_set) for db_user_doc_set in db_user_doc_sets]

    def save_documents(self, documents):
        docs_with_order = [doc for doc in documents]
        db_docs = [self._to_db_doc(doc) for doc in docs_with_order]
        self._ds_client.put_multi(db_docs)
        db_doc_keys = [db_doc.key for db_doc in db_docs]
        for (doc, key) in zip(docs_with_order, db_doc_keys):
            doc._db_key = key  # pylint: disable=protected-access
            doc.key_urlsafe = _to_urlsafe(key)

    def _to_db_doc(self, doc):
        not_indexed = ('title', 'summary', 'feature_vector')
        db_doc = self._make_entity('Document', not_indexed)
        db_doc['url'] = doc.url
        db_doc['title'] = doc.title
        db_doc['summary'] = doc.summary
        db_doc['feature_vector'] = self._to_db_feature_vector(doc.feature_vector)
        db_doc['datetime'] = datetime.datetime.utcnow()
        return db_doc

    def get_doc_by_urlsafe_key(self, key):
        db_key = _to_key(urlsafe=key)
        db_doc = self._ds_client.get(db_key)
        return _to_doc(db_doc)

    def save_user_action_on_doc(self, user, document, action_on_doc):
        """
        :param user: frontendstructs.User
        :param document: frontendstructs.Document
        :param action_on_doc: frontendstructs.UserActionTypeOnDoc
        """
        db_action = self._to_db_user_action_on_doc(user, document, action_on_doc)
        self._ds_client.put(db_action)

    def _to_db_user_action_on_doc(self, user, document, action_on_doc):
        db_action = self._make_entity('UserActionOnDoc', not_indexed=())
        db_action['user_key'] = user._db_key  # pylint: disable=protected-access
        db_action['document_key'] = document._db_key  # pylint: disable=protected-access
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
        doc_keys = list(set(action['document_key'] for action in db_actions))
        docs = self._to_docs(doc_keys)
        doc_key_to_doc = dict(zip(doc_keys, docs))

        # 3) build result, from two above database results
        actions_by_user = [[] for _ in users]
        user_mail_to_index = dict(zip((user.email for user in users), range(len(users))))
        for db_action in db_actions:
            doc = doc_key_to_doc[db_action['document_key']]
            action = _to_user_action_on_doc(doc, db_action)
            user_index = user_mail_to_index.get(db_action['user_key'].name)
            if user_index is not None:  # because we did not filter query on users
                actions_by_user[user_index].append(action)
        return actions_by_user
