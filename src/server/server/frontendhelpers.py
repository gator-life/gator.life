#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib


class PasswordHelpers(object):

    @staticmethod
    def hash_password(password):
        return hashlib.sha512(password).hexdigest()

    @staticmethod
    def is_password_valid_for_user(user, password):
        return user.password == hashlib.sha512(password).hexdigest()
