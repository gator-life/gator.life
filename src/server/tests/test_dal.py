# coding=utf-8
import unittest
from google.appengine.ext import ndb
from google.appengine.ext import testbed
import server.dal as dal
import server.dbentities as db


class DalTests(unittest.TestCase):
    def setUp(self):
        # standard set of calls to initialize unit test ndb environment
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        ndb.get_context().clear_cache()


    def tearDown(self):
        self.testbed.deactivate()


    def test_get_user_documents(self):
        # ------ init database -----------
        doc1 = db.Document.make(url='url1', title='title1', summary=None)
        doc2 = db.Document.make(url='url2', title='title2', summary=None)
        ndb.put_multi([doc1, doc2])  # we must store docs before creating user to init key field
        user_id = 'user_id'
        user = db.User.make(user_id=user_id, google_user_id=None,
                            user_documents=[db.UserDocument.make(document=doc1, grade=1.0),
                                            db.UserDocument.make(document=doc2, grade=0.5)])
        user.put()

        # ------ tested method -----------
        docs = dal.get_user_documents(user_id)

        # ------ check result -----------
        self.assertEquals(2, len(docs))
        self.assertEquals('url1', docs[0].document.url)
        self.assertEquals('title1', docs[0].document.title)
        self.assertEquals(1.0, docs[0].grade)


if __name__ == '__main__':
    unittest.main()
