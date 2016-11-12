# -*- coding: utf-8 -*-

from hashlib import sha256
from passlib.hash import bcrypt_sha256 # pylint: disable=no-name-in-module


def hash_str(str_value):
    return sha256(str_value).hexdigest()


def hash_password(password):
    return bcrypt_sha256.encrypt(password, rounds=10)


def verify_password(password, hashed_password):
    return bcrypt_sha256.verify(password, hashed_password)
