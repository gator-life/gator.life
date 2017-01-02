#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep

import unittest
from _socket import timeout
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from environment import IS_DEV_ENV

# pylint: skip-file
# pylint: disable=duplicate-code doesn't work. Duplication will be removed
# when all app is migrated to react. Meanwhile we skip file as a workaround


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


class WebAppTests(unittest.TestCase):

    def _get_webpage(self):
        with_retry(lambda: self.browser.get(self.url_base))

    @staticmethod
    def _click(element):
        with_retry(element.click)

    def setUp(self):
        self.browser = webdriver.PhantomJS()
        self.browser.implicitly_wait(3)
        self.browser.set_page_load_timeout(60)
        self.url_base = 'http://localhost:3000' if IS_DEV_ENV else 'http://localhost:8080/react'

    def tearDown(self):
        self.browser.quit()

    def test_react_homepage_poc_request_backend_api(self):
        self._get_webpage()
        message = self.browser.find_element_by_name('message').text
        self.assertEquals(u'Welcome to React No', message)
        edit_email_button = self.browser.find_element_by_name('editEmail-button')
        self._click(edit_email_button)
        sleep(0.1)  #  100 ms delay
        message_after_click = self.browser.find_element_by_name('message').text
        self.assertEquals(u'Welcome to React test_API HELLO', message_after_click)


if __name__ == '__main__':
    unittest.main()
