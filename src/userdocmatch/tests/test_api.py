#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from common.datehelper import utcnow
from userdocmatch.dal import Dal
from userdocmatch.api import UserDocMatcher, Document, ActionTypeOnDoc
from userdocmatch.frontendstructs import Document as DalDoc, TopicModelDescription, FeatureSet, FeatureVector
from userdocmatch.frontendstructs import UserDocument as DalUserDoc
from userdocmatch.frontendstructs import UserActionTypeOnDoc as DalActionType


class UserDocMatcherTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()
        model_id = u'UserDocMatcherTests_model_id'
        model = TopicModelDescription.make_from_scratch(model_id, [[('w', 1)]])
        self.dal.topic_model.save(model)
        self.ref_feature_set_id = u'UserDocMatcherTests_ref_feature_set_id'
        self.dal.feature_set.save_feature_set(FeatureSet(self.ref_feature_set_id, ['f'], model_id))
        self.dal.feature_set.save_ref_feature_set_id(self.ref_feature_set_id)
        self.matcher = UserDocMatcher()

    def test_create_user(self):
        # Only this test because it's properly tested
        # in structinit class
        interests = [
            u't1 t2',
            u't3'
        ]
        user_id = u'user_id_test_create_user'
        self.matcher.create_user(user_id, interests)
        user = self.dal.user.get_user(user_id)
        self.assertEquals(user_id, user.user_id)

    def test_get_url(self):
        url_hash = u'hash_test_get_url'
        url = u'test_get_url'
        dal_docs = [DalDoc(
            url,
            url_hash,
            None, None, FeatureVector([1.0], self.ref_feature_set_id)
        )]
        self.dal.doc.save_documents(dal_docs)
        result = self.matcher.get_url(url_hash)
        self.assertEquals(url, result)

    def test_get_docs(self):
        url_hash = u'hash_test_get_docs'
        url = u'url_test_get_docs'
        user_id = u'user_id_test_get_docs'
        title = u't1'
        summary = u's1'
        dal_doc = DalDoc(url, url_hash, title, summary, FeatureVector([1.0], self.ref_feature_set_id))
        dal_docs = [dal_doc]
        self.dal.doc.save_documents(dal_docs)
        interests = [u't1 t2', u't3']
        self.matcher.create_user(user_id, interests)

        user = self.dal.user.get_user(user_id)
        user_docs = [
            DalUserDoc(dal_doc, 0.5)
        ]
        self.dal.user_doc.save_user_docs(user, user_docs)
        docs = self.matcher.get_docs(user_id)
        self.assertEquals(1, len(docs))
        doc = docs[0]
        self.assertIsInstance(doc, Document)
        self.assertEquals(title, doc.title)
        self.assertEquals(summary, doc.summary)
        self.assertEquals(url, doc.url)
        self.assertEquals(url_hash, doc.url_hash)

    def test_add_user_action(self):
        now = utcnow()
        action = ActionTypeOnDoc.click_link
        user_id = u'test_add_user_action_user_id'
        self.matcher.create_user(user_id, [])
        url_hash = u'url_hash_test_add_user_action'
        dal_doc = DalDoc(u'u', url_hash, u't', u's', FeatureVector([1.0], self.ref_feature_set_id))
        self.dal.doc.save_documents([dal_doc])
        self.matcher.add_user_action(user_id, url_hash, action)
        actions = self.dal.user_action.get_user_actions_on_docs([user_id], now)[0]
        self.assertEquals(1, len(actions))
        action = actions[0]
        self.assertEquals(url_hash, action.document.url_hash)
        self.assertEquals(DalActionType.click_link, action.action_type)
        self.assertEquals(url_hash, action.document.url_hash)


if __name__ == '__main__':
    unittest.main()
