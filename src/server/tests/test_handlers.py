#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import Flask
import server.frontendstructs as struct
import server.handlers as handlers
import server.passwordhelpers as pswd


class DalUserMock(object):

    def __init__(self):
        self.saved_user = None
        self.saved_password = None

    def get_user(self, email):  # pylint: disable=unused-argument, no-self-use
        if email == 'mark':
            return struct.User.make_from_scratch(email, ['soccer', 'tuning'])
        return self.saved_user

    def save_user(self, user, password):
        self.saved_user = user
        self.saved_password = password

    def get_user_and_password(self, email):  # pylint: disable=unused-argument, no-self-use
        if email == 'mark':
            return (self.get_user(email), pswd.hash_password('dadada'))


class DalUserDocMock(object):

    def get_user_docs(self, user):  # pylint: disable=unused-argument, no-self-use
        def build_user_doc(title):
            return struct.UserDocument.make_from_scratch(
                struct.Document.make_from_scratch(None, None, title, None, None),
                0.0)

        if user.email == 'mark':
            return \
                [build_user_doc('title1'),
                 build_user_doc('title2')]
        if user.email == 'elon':
            return [
                build_user_doc('rocket')]
        return None


class DalFeatureSetMock(object):

    @staticmethod
    def get_ref_feature_set_id():
        return 'ref_feature_set_DalFeatureSetMock'

    def get_feature_set(self, feature_set_id):
        if feature_set_id == self.get_ref_feature_set_id():
            return struct.FeatureSet.make_from_db(feature_set_id, ['label1'], None)
        return None


class DalUserComputedProfileMock(object):

    def __init__(self):
        self.user_computed_profiles = None

    def save_user_computed_profiles(self, user_profile_list):
        self.user_computed_profiles = user_profile_list


class DalDocMock(object):

    def get_doc(self, url_hash):  # pylint: disable=unused-argument, no-self-use
        if url_hash == 'url_hash':
            return struct.Document.make_from_scratch('url3', None, 'title3', None, None)
        return None


class DalUserActionMock(object):

    def __init__(self):
        self.saved_user_doc_action_tuple = None

    def save_user_action_on_doc(self, user, document, action_on_doc):
        self.saved_user_doc_action_tuple = (user, document, action_on_doc)


class DalMock(object):

    def __init__(self):
        self.user_action = DalUserActionMock()
        self.doc = DalDocMock()
        self.user_computed_profile = DalUserComputedProfileMock()
        self.feature_set = DalFeatureSetMock()
        self.user_doc = DalUserDocMock()
        self.user = DalUserMock()


class HandlersTests(unittest.TestCase):

    def setUp(self):
        test_app = Flask("HandlersTests_flask_app")
        test_app.register_blueprint(handlers.handlers)
        test_app.secret_key = 'HandlersTests_flask_secret_key'
        self.app = test_app.test_client()
        test_app.config['TESTING'] = True
        self.dal = DalMock()
        handlers.DAL = self.dal

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
        response = self.app.post('/login', data=dict(email='mark', password='dadada'), follow_redirects=True)
        self._assert_is_home(response)

    def test_login_post_invalid_redirect_login(self):
        response = self.app.post('/login', data=dict(email='mark', password='JoIsNoOne'), follow_redirects=True)
        self._assert_is_login(response)
        self.assertTrue('Unknown email or invalid password' in response.data)

    def test_disconnect_disconnect_and_redirect_login(self):
        self._login()
        response = self.app.get('/disconnect', follow_redirects=True)
        with self.app.session_transaction() as session:
            self.assertFalse('email' in session)
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
        response = self.app.post('/register', data=dict(email='mark', password='', interests=''), follow_redirects=True)
        self._assert_is_register(response)
        self.assertTrue('This account already exists' in response.data)

    def test_register_post_with_new_email_save_profile_redirect_homepage(self):
        post_data = dict(email='elon', password='elon', interests='rockets\r\ncars')
        response = self.app.post('/register', data=post_data, follow_redirects=True)
        self.assertEquals('elon', self.dal.user.saved_user.email)
        self.assertEquals(['rockets', 'cars'], self.dal.user.saved_user.interests)
        self.assertEquals(1, len(self.dal.user_computed_profile.user_computed_profiles))
        self.assertEquals(pswd.hash_password('elon'), self.dal.user.saved_password)
        self._assert_is_home_elon(response)

    def test_link_with_user_not_connected_redirect_login(self):
        response = self.app.get('/link/1/key', follow_redirects=True)
        self._assert_is_login(response)

    def test_link_with_click_link_save_action_and_redirect(self):
        self._login()
        response = self.app.get('/link/3/url_hash', follow_redirects=False)
        action = self.dal.user_action.saved_user_doc_action_tuple[2]
        self.assertEquals(struct.UserActionTypeOnDoc.click_link, action)
        self.assertTrue('redirected' in response.data)
        self.assertTrue('url3' in response.data)

    def test_link_with_down_vote_link_save_action_stay_home(self):
        self._login()
        response = self.app.get('/link/2/url_hash', follow_redirects=True)

        user = self.dal.user_action.saved_user_doc_action_tuple[0]
        doc = self.dal.user_action.saved_user_doc_action_tuple[1]
        action = self.dal.user_action.saved_user_doc_action_tuple[2]

        self.assertEquals('mark', user.email)
        self.assertEquals('title3', doc.title)
        self.assertEquals(struct.UserActionTypeOnDoc.down_vote, action)
        self._assert_is_home(response)

    def _login(self):
        with self.app.session_transaction() as session:
            session['email'] = 'mark'

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
