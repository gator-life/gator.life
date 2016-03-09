"""
DAL (Data Access Layer) module
abstract database scheme and ndb API to communicate with the rest of the package through pure (not ndb) Python objects
"""
from google.appengine.ext import ndb
import dbentities as db  # pylint: disable=relative-import
import frontendstructs as struct  # pylint: disable=relative-import
# problem (to solve) with app engine: server is not seen as a package by GAE
# so you can't do proper relative import (from . import dbentities) as expected by pylint / pep8


def get_user(email):
    db_user = db.User.get(email)
    return _to_user(db_user) if db_user else None

def get_user_by_checking_password(email, password):
    user = get_user(email)
    if user is not None and user.password == password:
        return user
    return None

def _to_user(db_user):
    return struct.User.make_from_db(
        email=db_user.key.id(),
        password=db_user.password,
        interests=db_user.interests,
        user_doc_set_db_key=db_user.user_document_set_key,
        user_computed_profile_db_key=db_user.user_computed_profile_key)


def get_all_users():
    all_users_query = db.User.query()
    return [_to_user(db_user) for db_user in all_users_query.iter()]


def save_user(user):
    """
    save a user into the database, if it's newly created, db_keys will be initialized
    """
    if user._user_doc_set_db_key is None:  # pylint: disable=protected-access
        user._user_doc_set_db_key = db.UserDocumentSet.make().put()  # pylint: disable=protected-access
    if user._user_computed_profile_db_key is None:  # pylint: disable=protected-access
        null_feature_vector = db.FeatureVector.make(NULL_FEATURE_SET, [])
        null_model_data = db.UserProfileModelData.make([], [], 0., 0.)
        profile_key = db.UserComputedProfile.make(null_feature_vector, null_model_data).put()
        user._user_computed_profile_db_key = profile_key  # pylint: disable=protected-access
    db_user = _to_db_user(user)
    db_user.put()


def _to_db_user(user):
    db_user = db.User.make(user_id=user.email,
                           password=user.password,
                           interests=user.interests,
                           user_document_set_key=user._user_doc_set_db_key,  # pylint: disable=protected-access
                           user_computed_profile_key=user._user_computed_profile_db_key)  # pylint: disable=protected-access
    return db_user


def get_features(feature_set_id):
    db_feature_set = db.FeatureSet.get(feature_set_id)
    return [feature.name for feature in db_feature_set.features]


def save_features(feature_set_id, feature_names):
    features = [db.FeatureDescription.make(name) for name in feature_names]
    feature_set = db.FeatureSet.make(feature_set_id=feature_set_id, feature_descriptions=features)
    feature_set.put()


def _to_db_user_profile_model_data(user_profile_model_data):
    return db.UserProfileModelData.make(
        user_profile_model_data.positive_feedback_vector,
        user_profile_model_data.negative_feedback_vector,
        user_profile_model_data.positive_feedback_sum_coeff,
        user_profile_model_data.negative_feedback_sum_coeff
    )


def _to_db_computed_user_profile(user_computed_profile):
    db_feature_vector = _to_db_feature_vector(user_computed_profile.feature_vector)
    db_model_data = _to_db_user_profile_model_data(user_computed_profile.model_data)
    return db.UserComputedProfile.make(db_feature_vector, db_model_data)


def save_computed_user_profile(user, user_computed_profile):
    save_computed_user_profiles([(user, user_computed_profile)])


def save_computed_user_profiles(user_profile_list):
    """
    :param user_profile_list: list of tuples (struct.User, struct.UserComputedProfile)
    :return:
    """
    db_profiles = []
    for user, computed_user_profile in user_profile_list:
        db_profile = _to_db_computed_user_profile(computed_user_profile)
        # by setting as key the key previously referenced by the user, we will overwrite the previous profile in db
        db_profile.key = user._user_computed_profile_db_key  # pylint: disable=protected-access
        db_profiles.append(db_profile)
    ndb.put_multi(db_profiles)


def _to_user_profile_model_data(db_user_profile_model_data):
    return struct.UserProfileModelData.make_from_db(
        db_user_profile_model_data.positive_feedback_vector,
        db_user_profile_model_data.negative_feedback_vector,
        db_user_profile_model_data.positive_feedback_sum_coeff,
        db_user_profile_model_data.negative_feedback_sum_coeff
    )


def _to_user_computed_profile(db_user_computed_profile):
    model_data = _to_user_profile_model_data(db_user_computed_profile.model_data)
    feature_vector = _to_feature_vector(db_user_computed_profile.feature_vector)
    datetime = db_user_computed_profile.datetime
    return struct.UserComputedProfile.make_from_db(feature_vector, model_data, datetime)


def get_user_computed_profiles(users):
    keys = [user._user_computed_profile_db_key for user in users]  # pylint: disable=protected-access
    db_profiles = ndb.get_multi(keys)
    profiles = [_to_user_computed_profile(db_profile) for db_profile in db_profiles]
    return profiles


def get_user_feature_vector(user):
    return get_users_feature_vectors([user])[0]


def get_users_feature_vectors(users):
    # NB: this could be probably optimized by projection query if we need, but it would require to index vector property.
    profiles = get_user_computed_profiles(users)
    return [profile.feature_vector for profile in profiles]


def _to_feature_vector(db_feature_vector):
    vector = db_feature_vector.vector
    feature_set_id = db_feature_vector.feature_set_key.id()
    return struct.FeatureVector.make_from_scratch(vector=vector, feature_set_id=feature_set_id)


def _to_db_feature_vector(feature_vector):
    return db.FeatureVector.make(feature_vector.feature_set_id, vector=feature_vector.vector)


def _to_user_docs(db_user_docs):
    db_doc_keys = [user_doc.document_key for user_doc in db_user_docs]
    docs = _to_docs(db_doc_keys)
    user_docs = [struct.UserDocument.make_from_scratch(
        document=doc, grade=user_doc.grade) for doc, user_doc in zip(docs, db_user_docs)]
    return user_docs


def _to_docs(db_doc_keys):
    db_docs = ndb.get_multi(db_doc_keys)
    docs = (_to_doc(db_doc) for db_doc in db_docs)
    return docs


def _to_doc(db_doc):
    return struct.Document.make_from_db(
        url=db_doc.url, title=db_doc.title, summary=db_doc.summary, datetime=db_doc.datetime, db_key=db_doc.key,
        feature_vector=_to_feature_vector(db_doc.feature_vector))


def save_user_docs(user, user_docs):
    db_user_doc_set = user._user_doc_set_db_key.get()  # pylint: disable=protected-access
    db_user_docs = _to_db_user_docs(user_docs)
    db_user_doc_set.user_documents = db_user_docs
    db_user_doc_set.put()


def _to_db_user_docs(user_docs):
    db_user_docs = [
        db.UserDocument.make(
            document_key=user_doc.document._db_key,  # pylint: disable=protected-access
            grade=user_doc.grade
        ) for user_doc in user_docs]
    return db_user_docs


def save_users_docs(user_to_user_docs_list):
    """
    Save UserDocuments list associated to each User
    :param user_to_user_docs_list: list of tuples (User, List of UserDocument)
    """
    user_set_db_keys = []
    users_docs = []
    for user, user_docs in user_to_user_docs_list:
        user_set_db_keys.append(user._user_doc_set_db_key)  # pylint: disable=protected-access
        users_docs.append(user_docs)
    db_user_sets = ndb.get_multi(user_set_db_keys)
    for (db_user_set, user_docs) in zip(db_user_sets, users_docs):  # zip is ok because ndb.get_multi() maintains order
        db_user_set.user_documents = _to_db_user_docs(user_docs)
    ndb.put_multi(db_user_sets)


def get_user_docs(user):
    user_doc_set = user._user_doc_set_db_key.get()  # pylint: disable=protected-access
    return _to_user_docs(user_doc_set.user_documents)


def get_users_docs(users):
    db_user_doc_sets = ndb.get_multi(user._user_doc_set_db_key for user in users)  # pylint: disable=protected-access
    doc_keys_set = {user_doc.document_key for user_doc_set in db_user_doc_sets for user_doc in user_doc_set.user_documents}
    doc_keys_list = list(doc_keys_set)
    docs = _to_docs(doc_keys_list)
    keys_to_docs = dict(zip(doc_keys_list, docs))

    def to_user_doc(db_user_doc):
        return struct.UserDocument.make_from_db(keys_to_docs[db_user_doc.document_key], db_user_doc.grade)

    def db_set_to_user_doc_list(user_doc_set):
        return [to_user_doc(db_user_doc) for db_user_doc in user_doc_set.user_documents]

    return [db_set_to_user_doc_list(db_user_doc_set) for db_user_doc_set in db_user_doc_sets]


def save_documents(documents):
    docs_with_order = [doc for doc in documents]
    db_docs = [_to_db_doc(doc) for doc in docs_with_order]
    db_doc_keys = ndb.put_multi(db_docs)
    for (doc, key) in zip(docs_with_order, db_doc_keys):
        doc._db_key = key  # pylint: disable=protected-access


def _to_db_doc(doc):
    return db.Document.make(
        url=doc.url, title=doc.title, summary=doc.summary,
        feature_vector=_to_db_feature_vector(doc.feature_vector))


def get_doc_by_urlsafe_key(key):
    db_key = ndb.Key(urlsafe=key)
    return _to_doc(db_key.get())


def save_user_action_on_doc(user, document, action_on_doc):
    """
    :param user: frontendstructs.User
    :param document: frontendstructs.Document
    :param action_on_doc: frontendstructs.UserActionTypeOnDoc
    """
    db_str_action = _to_db_action_type_on_doc(action_on_doc)
    db.UserActionOnDoc.make(user.email, document._db_key, db_str_action).put()  # pylint: disable=protected-access


def get_user_actions_on_docs(users, from_datetime):
    """
    :param users: list of frontendstructs.User
    :param from_datetime:
    :return: return a list matching users input list, each element is the list of frontendstructs.UserActionOnDoc
     for this user inserted after 'from_datetime'
    """
    # 1) retrieve actions from database
    actions_query = db.UserActionOnDoc.query(db.UserActionOnDoc.datetime > from_datetime)
    db_actions = actions_query.fetch(10000)
    # NB: we only filter on datetime (and not the users) on the query because you can't mix
    # an 'IN something' query with other filter in datastore.
    # Moreover, request with filter 'IN users' is limited to 30 elements and is very inefficient
    # a long term solution if we need scalability is to replace users list by a range (min_user, max_user).
    # fetch(10000) is not scalable either, but I won't make something complex because I think
    # this second point would be solved if the first one (filter on user range) is solved

    # 2) retrieve docs present in actions from database
    doc_keys = list(set(action.document_key for action in db_actions))
    docs = _to_docs(doc_keys)
    doc_key_to_doc = dict(zip(doc_keys, docs))

    # 3) build result, from two above database results
    actions_by_user = [[] for _ in users]
    user_mail_to_index = dict(zip((user.email for user in users), range(len(users))))
    for db_action in db_actions:
        doc = doc_key_to_doc[db_action.document_key]
        action_type = to_user_action_type_on_doc(db_action.action_type)
        action = struct.UserActionOnDoc.make_from_db(doc, action_type, db_action.datetime)
        user_index = user_mail_to_index.get(db_action.user_key.id())
        if user_index is not None:  # because we did not filter query on users
            actions_by_user[user_index].append(action)
    return actions_by_user


def to_user_action_type_on_doc(user_action_on_doc_string):
    if user_action_on_doc_string == 'up_vote':
        return struct.UserActionTypeOnDoc.up_vote
    if user_action_on_doc_string == 'down_vote':
        return struct.UserActionTypeOnDoc.down_vote
    if user_action_on_doc_string == 'click_link':
        return struct.UserActionTypeOnDoc.click_link
    if user_action_on_doc_string == 'view_link':
        return struct.UserActionTypeOnDoc.view_link
    raise ValueError(user_action_on_doc_string + ' has no matching for Enum UserActionTypeOnDoc')

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


REF_FEATURE_SET = "ref_feature_set"
NULL_FEATURE_SET = "null_feature_set"
