#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib


def hash_password(password):
    return hashlib.sha512(password).hexdigest()


def is_password_valid_for_user(user_password, password):
    return user_password == hashlib.sha512(password).hexdigest()
