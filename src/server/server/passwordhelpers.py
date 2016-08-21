# -*- coding: utf-8 -*-

import hashlib


def hash_password(password):
    return hashlib.sha512(password.encode()).hexdigest()


def is_password_valid_for_user(user_password, password):
    return user_password == hash_password(password)
