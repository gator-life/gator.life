# -*- coding: utf-8 -*-

import hashlib
import os
import pickle


class UrlUnicityChecker(object):

    def __init__(self, persist_file):
        self._persist_file = persist_file
        self._hashed_urls = set()
        self._load()

    def is_unique_and_add(self, url):
        """
        If the url is unknown, add it to known urls and return true. Otherwise return false.
        :param url: An url
        """
        prev_len = len(self._hashed_urls)

        hashed_url = hashlib.md5(url.encode()).hexdigest()
        self._hashed_urls.add(hashed_url)

        new_len = len(self._hashed_urls)

        return prev_len != new_len

    def save(self):
        with open(self._persist_file, 'wb') as file_desc:
            pickle.dump(self._hashed_urls, file_desc)

    def _load(self):
        if os.path.isfile(self._persist_file):
            with open(self._persist_file, 'rb') as file_desc:
                self._hashed_urls = pickle.load(file_desc)
