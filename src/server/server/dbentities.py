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
    def make(document, grade):
        return UserDocument(document_key=document.key, grade=grade)


class User(ndb.Model):
    google_user_id = ndb.StringProperty(indexed=True, required=False)
    user_documents = ndb.StructuredProperty(UserDocument, repeated=True)

    @staticmethod
    def make(user_id, google_user_id, user_documents):
        return User(id=user_id, google_user_id=google_user_id, user_documents=user_documents)

    @staticmethod
    def get(user_id):
        return User.get_by_id(user_id)


