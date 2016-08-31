#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import unittest
from _socket import timeout
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from server import frontendstructs as structs, passwordhelpers as passwordhelpers
from server.dal import Dal, REF_FEATURE_SET
from common.datehelper import utcnow
import daltesthelpers


def with_retry(action):
    """
    retry action 2 times in case of timeout
    workaround of a random bug (probably race condition) between travis, docker container, selenium and phantomJS
    probably related to https://github.com/travis-ci/travis-ci/issues/3251
    solution inspired by https://github.com/spacetelescope/asv/pull/290
    """
    for _ in range(3):
        try:
            action()
            break
        except (timeout, TimeoutException):
            pass
    else:
        raise timeout


class NewVisitorTests(unittest.TestCase):

    def _get_webpage(self):
        with_retry(lambda: self.browser.get('http://localhost:8080'))

    @staticmethod
    def _click(element):
        with_retry(element.click)

    @classmethod
    def setUpClass(cls):
        daltesthelpers.init_features_dummy(REF_FEATURE_SET)

    def setUp(self):
        self.browser = webdriver.PhantomJS()
        self.browser.implicitly_wait(3)
        self.browser.set_page_load_timeout(60)
        self.dal = Dal()

    def tearDown(self):
        self.browser.quit()

    def _login(self, email, password):
        login_input_elt = self.browser.find_element_by_name('email')
        login_input_elt.send_keys(email)
        password_input_elt = self.browser.find_element_by_name('password')
        password_input_elt.send_keys(password)
        login_button = self.browser.find_element_by_name('login-button')
        self._click(login_button)

    def _register(self, email, password, interests):
        login_input_elt = self.browser.find_element_by_name('email')
        login_input_elt.send_keys(email)
        password_input_elt = self.browser.find_element_by_name('password')
        password_input_elt.send_keys(password)
        interests_input_elt = self.browser.find_element_by_name('interests')
        interests_input_elt.send_keys(interests)
        register_button = self.browser.find_element_by_name('register-button')
        self._click(register_button)

    def test_login_with_unknown_email(self):
        self._get_webpage()
        self._login('unknown@email.com', 'unknownpassword')
        error_message = self.browser.find_element_by_name('error-message').text
        self.assertEquals('Unknown email or invalid password', error_message)

    def test_login_with_invalid_password(self):
        daltesthelpers.create_user_dummy('known_user@gator.com', '', [''])
        self._get_webpage()
        self._login('known_user@gator.com', 'invalid_password')
        error_message = self.browser.find_element_by_name('error-message').text
        self.assertEquals('Unknown email or invalid password', error_message)

    def test_register(self):
        self._get_webpage()
        register_link = self.browser.find_element_by_link_text('Register')
        self._click(register_link)

        # An unique email is generated at each run to avoid a failure of the test if it's launched twice on
        # the same instance of GAE (it's launching twice on Travis).
        email = 'register_' + str(int(time.time())) + '@gator.com'

        interests_str = 'finance\npython\ncomputer science'
        self._register(email, 'password', interests_str)

        user = self.dal.get_user(email)
        self.assertIsNotNone(user)
        self.assertItemsEqual(user.interests, interests_str.splitlines())
        self.assertItemsEqual(user.interests, interests_str.splitlines())

        # If the user as been successfully registered, it should be redirected to home page
        self.assertEqual('http://localhost:8080/', self.browser.current_url)

    def test_register_with_a_known_email(self):
        daltesthelpers.create_user_dummy('test_register_with_a_known_email@gator.com', '', [''])

        self._get_webpage()

        register_link = self.browser.find_element_by_link_text('Register')
        self._click(register_link)

        self._register('test_register_with_a_known_email@gator.com', 'password', 'interests')

        error_message = self.browser.find_element_by_name('error-message').text
        self.assertEquals('This account already exists', error_message)

    def test_login_and_do_actions(self):
        now = utcnow()
        email = 'kevin@gator.com'
        password = 'kevintheboss'

        user = daltesthelpers.create_user_dummy(email, passwordhelpers.hash_password(password),
                                                interests=['lol', 'xpdr', 'trop lol'])

        self._get_webpage()

        self._login(email, password)

        self.assertEquals('Gator Life !', self.browser.title)

        title = self.browser.find_element_by_name('title').text
        subtitle = self.browser.find_element_by_name('subtitle').text

        self.assertEquals('Gator.Life', title)
        self.assertEquals('The best of the web just for you ' + email + ' !', subtitle)

        disconnect_link = self.browser.find_elements_by_link_text('Disconnect')
        self.assertEquals(1, len(disconnect_link))

        # There is two links on the page and related up/down links : google.com, gator.life
        links = self.browser.find_elements_by_name('link')
        self.assertEqual(2, len(links))
        self.assertEqual('google.com', links[0].text)
        self.assertEqual('gator.life', links[1].text)

        # Click on up for first link & down for the second link
        up_vote_links = self.browser.find_elements_by_name('up-vote')
        self.assertEqual(2, len(up_vote_links))
        up_link = up_vote_links[0]
        self._click(up_link)

        down_vote_links = self.browser.find_elements_by_name('down-vote')

        self.assertEqual(2, len(down_vote_links))
        down_link = down_vote_links[1]
        self._click(down_link)

        # Click on google.com and wait to go there, if it worked, 'google' is the tab title
        # Note that an object referencing an element of the webpage (eg. a link) is not valid when a click is done,
        # T hus we need to retrieve links to click on google.
        links = self.browser.find_elements_by_name('link')

        google_link = links[0]
        self._click(google_link)
        self.assertEqual("Google", self.browser.title)

        actions_by_user = self.dal.get_user_actions_on_docs([user], now)

        actions = actions_by_user[0]
        self.assertEqual(3, len(actions))

        actions_as_tuples = [(action.document.url, action.action_type) for action in actions]

        self.assertTrue(('https://www.google.com', structs.UserActionTypeOnDoc.up_vote) in actions_as_tuples)
        self.assertTrue(('gator.life', structs.UserActionTypeOnDoc.down_vote) in actions_as_tuples)
        self.assertTrue(('https://www.google.com', structs.UserActionTypeOnDoc.click_link) in actions_as_tuples)


if __name__ == '__main__':
    unittest.main()
