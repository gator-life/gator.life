# -*- coding: utf-8 -*-

import hashlib


def hash_safe(str_value):
    return hashlib.sha256(str_value).hexdigest()
