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


def _to_user(db_user):
    return struct.User.make_from_db(
        email=db_user.key.id(),
        user_doc_set_db_key=db_user.user_document_set_key,
        feature_vector_db_key=db_user.feature_vector_key)


def get_all_users():
    all_users_query = db.User.query()
    return [_to_user(db_user) for db_user in all_users_query.iter()]


def save_user(user):
    """
    save a user into the database, if it's newly created, db_keys will be initialized
    """
    if user.user_doc_set_db_key is None:
        user.user_doc_set_db_key = db.UserDocumentSet.make().put()
    if user.feature_vector_db_key is None:
        user.feature_vector_db_key = db.FeatureVector.make(NULL_FEATURE_SET, []).put()

    db_user = _to_db_user(user)
    db_user.put()


def _to_db_user(user):
    db_user = db.User.make(user_id=user.email,
                           google_user_id=None,
                           user_document_set_key=user.user_doc_set_db_key,
                           feature_vector_key=user.feature_vector_db_key)
    return db_user


def get_features(feature_set_id):
    db_feature_set = db.FeatureSet.get(feature_set_id)
    return [feature.name for feature in db_feature_set.features]


def save_user_feature_vector(user, feature_vector):
    db_feature_vector = _to_db_feature_vector(feature_vector)
    db_feature_vector.key = user.feature_vector_db_key
    db_feature_vector.put()


def get_user_feature_vector(user):
    return _to_feature_vector(user.feature_vector_db_key.get())


def _to_feature_vector(db_feature_vector):
    vector = db_feature_vector.vector
    feature_set_db_key = db_feature_vector.feature_set_key
    feature_set = feature_set_db_key.get()
    labels = [feature.name for feature in feature_set.features]
    return struct.FeatureVector(vector=vector, labels=labels, feature_set_id=feature_set_db_key.id())


def _to_db_feature_vector(feature_vector):
    return db.FeatureVector.make(feature_vector.feature_set_id, vector=feature_vector.vector)


def _to_user_docs(db_user_docs):
    db_doc_keys = [user_doc.document_key for user_doc in db_user_docs]
    db_docs = ndb.get_multi(db_doc_keys)
    docs = (struct.Document.make_from_db(
        url=db_doc.url, title=db_doc.title, summary=db_doc.summary, date=db_doc.date, db_key=db_doc.key)
            for db_doc in db_docs)
    user_docs = [struct.UserDocument(document=doc, grade=user_doc.grade) for doc, user_doc in zip(docs, db_user_docs)]
    return user_docs


def save_user_docs(user, user_docs):
    db_user_docs = [
        db.UserDocument.make(document_key=user_doc.document.db_key, grade=user_doc.grade) for user_doc in user_docs]
    user_doc_set = user.user_doc_set_db_key.get()
    user_doc_set.user_documents = db_user_docs
    user_doc_set.put()


def get_user_docs(user):
    user_doc_set = user.user_doc_set_db_key.get()
    return _to_user_docs(user_doc_set.user_documents)


def save_documents(documents):
    docs_with_order = [doc for doc in documents]
    db_docs = [db.Document.make(url=doc.url, title=doc.title, summary=doc.summary) for doc in docs_with_order]
    db_doc_keys = ndb.put_multi(db_docs)
    for (doc, key) in zip(documents, db_doc_keys):
        doc.db_key = key


# should be deleted, just to mock input from scraper/learner
def init_user_dummy(user_id):
    dummy_doc1 = struct.Document.make_from_scratch(
        url='https://www.google.com', title='google.com', summary='we will buy you')
    dummy_doc2 = struct.Document.make_from_scratch(
        url='gator.life', title='gator.life', summary='YGNI')
    save_documents([dummy_doc1, dummy_doc2])

    new_user = struct.User.make_from_scratch(email=user_id)
    save_user(new_user)
    user_doc1 = struct.UserDocument(document=dummy_doc1, grade=1.0)
    user_doc2 = struct.UserDocument(document=dummy_doc2, grade=0.5)
    save_user_docs(new_user, [user_doc1, user_doc2])
    return new_user


# should be deleted, just to mock input from scraper/learner
def init_features_dummy(feature_set_id):
    feature_names = ['sport', 'trading', 'bmw', 'c++']
    features = [db.FeatureDescription.make(name) for name in feature_names]
    feature_set = db.FeatureSet.make(feature_set_id=feature_set_id, feature_descriptions=features)
    feature_set.put()


def init_null_feature_set():
    db.FeatureSet.make(NULL_FEATURE_SET, []).put()

NEW_USER_ID = "new_user_id"
REF_FEATURE_SET = "ref_feature_set"
NULL_FEATURE_SET = "null_feature_set"
