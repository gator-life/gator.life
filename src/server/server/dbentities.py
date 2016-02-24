"""
NDB datastore entities (DB scheme)
this module should not be included except from dal.py
"""
from google.appengine.ext import ndb


# ----------- entities modified by backend -----------

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


class Document(ndb.Model):
    url = ndb.StringProperty(indexed=False, required=True)  # NB: url cannot be the key because it's 500 bytes max
    title = ndb.StringProperty(indexed=False, required=True)
    summary = ndb.StringProperty(indexed=False, required=False)
    datetime = ndb.DateTimeProperty(indexed=False, required=True, auto_now_add=True)
    feature_vector = ndb.StructuredProperty(FeatureVector, indexed=False, repeated=False, required=True)

    @staticmethod
    def make(url, title, summary, feature_vector):
        return Document(url=url, title=title, summary=summary, feature_vector=feature_vector)


class UserDocument(ndb.Model):
    document_key = ndb.KeyProperty(kind=Document, indexed=False, required=True)
    grade = ndb.FloatProperty(indexed=False, required=True)

    @staticmethod
    def make(document_key, grade):
        return UserDocument(document_key=document_key, grade=grade)


class UserDocumentSet(ndb.Model):
    user_documents = ndb.StructuredProperty(UserDocument, indexed=False, repeated=True)

    @staticmethod
    def make():
        return UserDocumentSet(user_documents=[])

    def set_user_documents(self, user_documents):
        self.user_documents = user_documents


# ----------- entities modified by frontend -----------

class User(ndb.Model):
    password = ndb.StringProperty(indexed=False, required=True)
    interests = ndb.StringProperty(indexed=False, required=True)
    user_document_set_key = ndb.KeyProperty(UserDocumentSet, indexed=False, required=True)
    feature_vector_key = ndb.KeyProperty(FeatureVector, repeated=False, required=True)

    @staticmethod
    def make(user_id, password, interests, user_document_set_key, feature_vector_key):
        return User(
            id=user_id,
            password=password,
            interests=interests,
            user_document_set_key=user_document_set_key,
            feature_vector_key=feature_vector_key)

    @staticmethod
    def get(user_id):
        return User.get_by_id(user_id)


class UserActionOnDoc(ndb.Model):
    document_key = ndb.KeyProperty(kind=Document, indexed=False, required=True)
    user_key = ndb.KeyProperty(kind=User, indexed=True, required=True)
    action_type = ndb.StringProperty(indexed=False, required=True)
    datetime = ndb.DateTimeProperty(indexed=True, required=True, auto_now_add=True)

    @staticmethod
    def make(user_id, document_key, action_type):
        return UserActionOnDoc(user_key=ndb.Key(User, user_id), document_key=document_key, action_type=action_type)
