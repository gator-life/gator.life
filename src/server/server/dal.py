"""
DAL (Data Access Layer) module
abstract database scheme and ndb API to communicate with the rest of the package through pure (not ndb) Python objects
"""
from google.appengine.ext import ndb
import dbentities as db  # pylint: disable=relative-import
# problem (to solve) with app engine: server is not seen as a package by GAE
# so you can't do proper relative import (from . import dbentities) as expected by pylint / pep8


class Document(object):
    def __init__(self, url, title, db_key):
        self.url = url
        self.title = title
        self.db_key = db_key


class UserDocument(object):
    def __init__(self, document, grade):
        self.document = document
        self.grade = grade


class User(object):
    def __init__(self, email, user_docs, feature_vector):
        self.email = email
        self.user_docs = user_docs
        self.feature_vector = feature_vector


class FeatureVector(object):
    def __init__(self, vector, labels, feature_set_id):
        self.vector = vector
        self.labels = labels
        self.feature_set_id = feature_set_id


def get_user(email):
    db_user = db.User.get(email)
    if db_user is None:
        return None

    user_docs = _to_user_docs(db_user.user_documents)
    feature_vector = _to_feature_vector(db_user.feature_vector)

    return User(email=email, user_docs=user_docs, feature_vector=feature_vector)


def save_user(user):
    db_user_docs = _to_db_user_docs(user.user_docs)
    db_feature_vector = _to_db_feature_vector(user.feature_vector)

    db_user = db.User.make(user_id=user.email,
                           google_user_id=None,
                           user_documents=db_user_docs,
                           feature_vector=db_feature_vector)
    db_user.put()


def get_features(feature_set_id):
    db_feature_set = db.FeatureSet.get(feature_set_id)
    return [feature.name for feature in db_feature_set.features]


def _to_feature_vector(db_feature_vector):
    if db_feature_vector is None:
        return None

    vector = db_feature_vector.vector
    feature_set_db_key = db_feature_vector.feature_set_key
    labels = [feature.name for feature in feature_set_db_key.get().features]
    return FeatureVector(vector=vector, labels=labels, feature_set_id=feature_set_db_key.id())


def _to_user_docs(db_user_docs):
    db_doc_keys = [user_doc.document_key for user_doc in db_user_docs]
    db_docs = ndb.get_multi(db_doc_keys)
    docs = (Document(url=db_doc.url, title=db_doc.title, db_key=db_doc.key) for db_doc in db_docs)
    user_docs = [UserDocument(document=doc, grade=user_doc.grade) for doc, user_doc in zip(docs, db_user_docs)]
    return user_docs


def _to_db_user_docs(user_docs):
    return [db.UserDocument.make(document_key=user_doc.document.db_key, grade=user_doc.grade) for user_doc in user_docs]


def _to_db_feature_vector(feature_vector):
    return db.FeatureVector.make(feature_vector.feature_set_id, vector=feature_vector.vector)


# should be deleted, just to mock input from scraper/learner
def init_user_dummy(user_id):
    dummy_doc1 = db.Document.make(url='https://www.google.com', title='google.com', summary='we will buy you')
    dummy_doc2 = db.Document.make(url='gator.life', title='gator.life', summary='YGNI')
    ndb.put_multi([dummy_doc1, dummy_doc2])  # we must store docs before creating user to init key field
    new_user = db.User.make(user_id=user_id,
                            google_user_id=None,
                            user_documents=[db.UserDocument.make(document_key=dummy_doc1.key, grade=1.0),
                                            db.UserDocument.make(document_key=dummy_doc2.key, grade=0.5)],
                            feature_vector=None)

    new_user.put()


# should be deleted, just to mock input from scraper/learner
def init_features_dummy(feature_set_id):
    feature_names = ['sport', 'trading', 'bmw', 'c++']
    features = [db.FeatureDescription.make(name) for name in feature_names]
    feature_set = db.FeatureSet.make(feature_set_id=feature_set_id, feature_descriptions=features)
    feature_set.put()


NEW_USER_ID = "new_user_id"

REF_FEATURE_SET = "ref_feature_set"
