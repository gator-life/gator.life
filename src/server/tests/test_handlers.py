#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from server.dal import REF_FEATURE_SET
import server.frontendstructs as struct
import server.handlers as handlers
import server.main as main
import server.passwordhelpers as pswd


class DalMock(object):

    def __init__(self):
        self.saved_user = None
        self.saved_password = None
        self.user_computed_profiles = None
        self.saved_user_doc_action_tuple = None

    def get_user(self, email):  # pylint: disable=unused-argument, no-self-use
        if email == 'mark':
            return struct.User.make_from_scratch(email, ['soccer', 'tuning'])
        return self.saved_user

    def get_user_docs(self, user):  # pylint: disable=unused-argument, no-self-use
        if user.email == 'mark':
            return \
                [struct.UserDocument.make_from_scratch(struct.Document.make_from_scratch(None, 'title1', None, None), 0.0),
                 struct.UserDocument.make_from_scratch(struct.Document.make_from_scratch(None, 'title2', None, None), 0.0)]
        if user.email == 'elon':
            return [
                struct.UserDocument.make_from_scratch(struct.Document.make_from_scratch(None, 'rocket', None, None), 0.0)]
        return None

    def save_user(self, user, password):
        self.saved_user = user
        self.saved_password = password

    def get_features(self, feature_set_id):  # pylint: disable=unused-argument, no-self-use
        if feature_set_id == REF_FEATURE_SET:
            return ['label1']
        return None

    def save_user_computed_profiles(self, user_profile_list):
        self.user_computed_profiles = user_profile_list

    def get_user_and_password(self, email):  # pylint: disable=unused-argument, no-self-use
        if email == 'mark':
            return (self.get_user(email), pswd.hash_password('dadada'))

    def get_doc_by_urlsafe_key(self, url_safe_key):  # pylint: disable=unused-argument, no-self-use
        if url_safe_key == 'url_safe_key':
            return struct.Document.make_from_scratch('url3', 'title3', None, None)
        return None

    def save_user_action_on_doc(self, user, document, action_on_doc):
        self.saved_user_doc_action_tuple = (user, document, action_on_doc)


class HandlersTests(unittest.TestCase):

    def setUp(self):
        self.app = main.APP.test_client()
        main.APP.config['TESTING'] = True
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
        self.assertTrue('Unknown email or invalid password' in response.data.decode())

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
        self.assertTrue('This account already exists' in response.data.decode())

    def test_register_post_with_new_email_save_profile_redirect_homepage(self):
        post_data = dict(email='elon', password='elon', interests='rockets\r\ncars')
        response = self.app.post('/register', data=post_data, follow_redirects=True)
        self.assertEqual('elon', self.dal.saved_user.email)
        self.assertEqual(['rockets', 'cars'], self.dal.saved_user.interests)
        self.assertEqual(1, len(self.dal.user_computed_profiles))
        self.assertEqual(pswd.hash_password('elon'), self.dal.saved_password)
        self._assert_is_home_elon(response)

    def test_link_with_user_not_connected_redirect_login(self):
        response = self.app.get('/link/1/key', follow_redirects=True)
        self._assert_is_login(response)

    def test_link_with_click_link_save_action_and_redirect(self):
        self._login()
        response = self.app.get('/link/3/url_safe_key', follow_redirects=False)
        action = self.dal.saved_user_doc_action_tuple[2]
        self.assertEqual(struct.UserActionTypeOnDoc.click_link, action)
        self.assertTrue('redirected' in response.data.decode())
        self.assertTrue('url3' in response.data.decode())

    def test_link_with_down_vote_link_save_action_stay_home(self):
        self._login()
        response = self.app.get('/link/2/url_safe_key', follow_redirects=True)

        user = self.dal.saved_user_doc_action_tuple[0]
        doc = self.dal.saved_user_doc_action_tuple[1]
        action = self.dal.saved_user_doc_action_tuple[2]

        self.assertEqual('mark', user.email)
        self.assertEqual('title3', doc.title)
        self.assertEqual(struct.UserActionTypeOnDoc.down_vote, action)
        self._assert_is_home(response)

    def _login(self):
        with self.app.session_transaction() as session:
            session['email'] = 'mark'

    def _assert_is_register(self, response):
        self.assertEqual(200, response.status_code)
        self.assertTrue('Register' in response.data.decode())
        self.assertTrue('interests' in response.data.decode())

    def _assert_is_home_elon(self, response):
        self.assertEqual(200, response.status_code)
        self.assertTrue('elon' in response.data.decode())
        self.assertTrue('rocket' in response.data.decode())

    def _assert_is_home(self, response):
        self.assertEqual(200, response.status_code)
        self.assertTrue('mark' in response.data.decode())
        self.assertTrue('title1' in response.data.decode())
        self.assertTrue('title2' in response.data.decode())

    def _assert_is_login(self, response):
        self.assertEqual(200, response.status_code)
        self.assertTrue('Login' in response.data.decode())
        self.assertTrue('email' in response.data.decode())
        self.assertTrue('password' in response.data.decode())

if __name__ == '__main__':
    unittest.main()
