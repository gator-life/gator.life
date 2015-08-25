"""
DAL (Data Access Layer) module
abstract database scheme and ndb API to communicate with the rest of the package through pure (not ndb) Python objects
"""
from google.appengine.ext import ndb
import dbentities as db  # pylint: disable=relative-import
# problem (to solve) with app engine: server is not seen as a package by GAE
# so you can't do proper relative import (from . import dbentities) as expected by pylint / pep8

class Document(object):
    def __init__(self, url, title):
        self.url = url
        self.title = title

class UserDocument(object):
    def __init__(self, document, grade):
        self.document = document
        self.grade = grade

def get_user_documents(user_id):
    db_user = db.User.get(user_id)
    db_doc_keys = [user_doc.document_key for user_doc in db_user.user_documents]
    db_docs = ndb.get_multi(db_doc_keys)
    docs = (Document(url=db_doc.url, title=db_doc.title) for db_doc in db_docs)
    user_docs = [UserDocument(document=doc, grade=user_doc.grade) for doc, user_doc in zip(docs, db_user.user_documents)]
    return user_docs

# should be deleted, just to mock input from scraper/learner
def init_user_dummy(user_id):
    dummy_doc1 = db.Document.make(url='https://www.google.com', title='google.com', summary='we will buy you')
    dummy_doc2 = db.Document.make(url='gator.life', title='gator.life', summary='YGNI')
    ndb.put_multi([dummy_doc1, dummy_doc2])  # we must store docs before creating user to init key field
    new_user = db.User.make(user_id=user_id, google_user_id=None,
                            user_documents=[db.UserDocument.make(document=dummy_doc1, grade=1.0),
                                            db.UserDocument.make(document=dummy_doc2, grade=0.5)])
    new_user.put()
