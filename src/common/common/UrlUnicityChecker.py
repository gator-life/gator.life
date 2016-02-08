# -*- coding: utf-8 -*-

import hashlib
import os
import pickle


class UrlUnicityChecker(object):

    def __init__(self, persist_file):
        self.persist_file = persist_file
        self.hashed_urls_set = set()
        self._load()

    def is_unique(self, url):
        prev_len = len(self.hashed_urls_set)

        hashed_url = hashlib.md5(url).hexdigest()
        self.hashed_urls_set.add(hashed_url)

        new_len = len(self.hashed_urls_set)

        return prev_len != new_len

    def save(self):
        with open(self.persist_file, 'wb') as file_desc:
            pickle.dump(self.hashed_urls_set, file_desc)

    def _load(self):
        if os.path.isfile(self.persist_file):
            with open(self.persist_file, 'rb') as file_desc:
                self.hashed_urls_set = pickle.load(file_desc)
