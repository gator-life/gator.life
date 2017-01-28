#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import Flask
from userdocmatch.api import Document, ActionTypeOnDoc
import server.handlers as handlers
from server.dalaccount import Account
import common.crypto as crypto


class DalAccountMock(object):

    def __init__(self):
        self.saved_account = None

    def exists(self, email):
        return self.try_get(email) is not None

    def create(self, account):
        account.account_id = account.email + u'_id'
        self.saved_account = account

    def try_get(self, email):
        if email == u'mark':
            return Account(email, crypto.hash_password(u'dadada'), email + u"_id")
        return self.saved_account


class UserDocMatcherMock(object):

    def __init__(self):
        self.saved_user_id = None
        self.saved_interests = None
        self.saved_user_doc_action_tuple = None

    @staticmethod
    def get_docs(user_id):
        def build_user_doc(title):
            return Document(title + u'hash', title + u'url', title, None)

        if user_id == u'mark_id':
            return \
                [build_user_doc(u'title1'),
                 build_user_doc(u'title2')]
        if user_id == u'elon_id':
            return [
                build_user_doc(u'rocket')]
        return None

    @staticmethod
    def get_url(url_hash):
        return url_hash.strip(u'hash') + u'url'

    def create_user(self, user_id, interests):
        self.saved_user_id = user_id
        self.saved_interests = interests

    def add_user_action(self, user_id, url_hash, action_type_on_doc):
        self.saved_user_doc_action_tuple = (user_id, url_hash, action_type_on_doc)


class HandlersTests(unittest.TestCase):

    def setUp(self):
        test_app = Flask("HandlersTests_flask_app")
        test_app.register_blueprint(handlers.handlers)
        test_app.secret_key = 'HandlersTests_flask_secret_key'
        self.app = test_app.test_client()
        test_app.config['TESTING'] = True
        self.user_doc_matcher = UserDocMatcherMock()
        handlers.USER_DOC_MATCHER = self.user_doc_matcher
        self.dal_account = DalAccountMock()
        handlers.get_dal_account = lambda: self.dal_account

    def test_home_without_user_render_login(self):
        response = self.app.get('/', follow_redirects=True)
        self._assert_is_login(response)

    def test_home_with_user_render_docs(self):
        self._login()
        response = self.app.get('/', follow_redirects=True)
        self._assert_is_home(response)

    def test_login_with_user_connected_redirect_home(self):
        self._login()
        response = self.app.get('/login', follow_redirects=True)
        self._assert_is_home(response)

    def test_login_post_valid_redirect_home(self):
        response = self.app.post('/login', data=dict(email=u'mark', password=u'dadada'), follow_redirects=True)
        self._assert_is_home(response)

    def test_login_post_invalid_redirect_login(self):
        response = self.app.post('/login', data=dict(email=u'mark', password=u'JoIsNoOne'), follow_redirects=True)
        self._assert_is_login(response)
        self.assertTrue('Unknown email or invalid password' in response.data)

    def test_disconnect_disconnect_and_redirect_login(self):
        self._login()
        response = self.app.get('/disconnect', follow_redirects=True)
        with self.app.session_transaction() as session:
            self.assertFalse('email' in session)
            self.assertFalse('user_id' in session)
        self._assert_is_login(response)

    def test_disconnect_not_connected_redirect_login(self):
        response = self.app.get('/disconnect', follow_redirects=True)
        self._assert_is_login(response)

    def test_register_get_without_user_display_register(self):
        response = self.app.get('/register', follow_redirects=True)
        self._assert_is_register(response)

    def test_register_get_with_user_redirect_home(self):
        self._login()
        response = self.app.get('/register', follow_redirects=True)
        self._assert_is_home(response)

    def test_register_post_with_user_redirect_home(self):
        self._login()
        response = self.app.post('/register', follow_redirects=True)
        self._assert_is_home(response)

    def test_register_post_with_existing_email(self):
        response = self.app.post('/register', data=dict(email=u'mark', password=u'', interests=u''), follow_redirects=True)
        self._assert_is_register(response)
        self.assertTrue('This account already exists' in response.data)

    def test_register_post_with_new_email_save_profile_redirect_homepage(self):
        post_data = dict(email=u'elon', password=u'elon', interests=u'rockets\r\ncars')
        response = self.app.post('/register', data=post_data, follow_redirects=True)

        self.assertEquals(u'elon_id', self.user_doc_matcher.saved_user_id)
        self.assertEquals(u'elon_id', self.dal_account.saved_account.account_id)
        self.assertEquals([u'rockets', u'cars'], self.user_doc_matcher.saved_interests)
        self.assertTrue(crypto.verify_password(u'elon', self.dal_account.saved_account.password_hash))
        self._assert_is_home_elon(response)

    def test_link_with_user_not_connected_redirect_login(self):
        response = self.app.get('/link/1/key', follow_redirects=True)
        self._assert_is_login(response)

    def test_link_with_click_link_save_action_and_redirect(self):
        self._login()
        response = self.app.get('/link/3/url_redirect_hash', follow_redirects=False)
        action = self.user_doc_matcher.saved_user_doc_action_tuple[2]
        self.assertEquals(ActionTypeOnDoc.click_link, action)
        self.assertTrue('redirected' in response.data)
        self.assertTrue('url_redirect_url' in response.data)

    def test_link_with_down_vote_link_save_action_stay_home(self):
        self._login()
        response = self.app.get('/link/2/url_hash', follow_redirects=True)

        user_id = self.user_doc_matcher.saved_user_doc_action_tuple[0]
        doc_url_hash = self.user_doc_matcher.saved_user_doc_action_tuple[1]
        action = self.user_doc_matcher.saved_user_doc_action_tuple[2]

        self.assertEquals(u'mark_id', user_id)
        self.assertEquals(u'url_hash', doc_url_hash)
        self.assertEquals(ActionTypeOnDoc.down_vote, action)
        self._assert_is_home(response)

    def _login(self):
        with self.app.session_transaction() as session:
            session['user_id'] = u'mark_id'
            session['email'] = u'mark'

    def _assert_is_register(self, response):
        self.assertEquals(200, response.status_code)
        self.assertTrue('Register' in response.data)
        self.assertTrue('interests' in response.data)

    def _assert_is_home_elon(self, response):
        self.assertEquals(200, response.status_code)
        self.assertTrue('elon' in response.data)
        self.assertTrue('rocket' in response.data)

    def _assert_is_home(self, response):
        self.assertEquals(200, response.status_code)
        self.assertTrue('mark' in response.data)
        self.assertTrue('title1' in response.data)
        self.assertTrue('title2' in response.data)

    def _assert_is_login(self, response):
        self.assertEquals(200, response.status_code)
        self.assertTrue('Login' in response.data)
        self.assertTrue('email' in response.data)
        self.assertTrue('password' in response.data)

if __name__ == '__main__':
    unittest.main()
