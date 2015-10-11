"""
NDB datastore entities (DB scheme)
this module should not be included except from dal.py
"""
from google.appengine.ext import ndb

class Document(ndb.Model):
    url = ndb.StringProperty(indexed=False, required=True)  # NB: url cannot be the key because it's 500 bytes max
    title = ndb.StringProperty(indexed=False, required=True)
    summary = ndb.StringProperty(indexed=False, required=False)
    date = ndb.DateTimeProperty(indexed=False, required=True, auto_now_add=True)

    @staticmethod
    def make(url, title, summary):
        return Document(url=url, title=title, summary=summary)


class UserDocument(ndb.Model):
    document_key = ndb.KeyProperty(kind=Document, indexed=False, required=True)
    grade = ndb.FloatProperty(indexed=False, required=True)

    @staticmethod
    def make(document_key, grade):
        return UserDocument(document_key=document_key, grade=grade)

class FeatureDescription(ndb.Model):
    name = ndb.StringProperty(indexed=False, required=True)

    @staticmethod
    def make(name):
        return FeatureDescription(name=name)

class FeatureSet(ndb.Model):
    features = ndb.StructuredProperty(FeatureDescription, indexed=False, repeated=True)

    @staticmethod
    def make(feature_set_id, feature_descriptions):
        return FeatureSet(id=feature_set_id, features=feature_descriptions)

    @staticmethod
    def get(feature_set_id):
        return FeatureSet.get_by_id(feature_set_id)


class FeatureVector(ndb.Model):
    vector = ndb.FloatProperty(indexed=False, repeated=True)
    feature_set_key = ndb.KeyProperty(kind=FeatureSet, indexed=False, required=True)

    @staticmethod
    def make(feature_set_id, vector):
        return FeatureVector(feature_set_key=ndb.Key(FeatureSet, feature_set_id), vector=vector)

class User(ndb.Model):
    google_user_id = ndb.StringProperty(indexed=True, required=False)
    user_documents = ndb.StructuredProperty(UserDocument, repeated=True)
    feature_vector = ndb.StructuredProperty(FeatureVector, repeated=False, required=False)

    @staticmethod
    def make(user_id, google_user_id, user_documents, feature_vector):
        return User(id=user_id, google_user_id=google_user_id, user_documents=user_documents, feature_vector=feature_vector)

    @staticmethod
    def get(user_id):
        return User.get_by_id(user_id)



