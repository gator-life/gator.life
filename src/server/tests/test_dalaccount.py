#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from server.dalaccount import DalAccount, Account


class DalAccountTests(unittest.TestCase):

    def setUp(self):
        self.dal = DalAccount()

    def test_exists_with_existing_return_true(self):
        account = create_account(u'test_exists_with_existing_return_true')
        self.dal.create(account)
        self.assertTrue(self.dal.exists(account.email))

    def test_exists_with_missing_return_false(self):
        self.assertFalse(self.dal.exists(u'missing_email'))

    def test_create_then_get(self):
        account = create_account(u'test_create_then_get')
        self.assertIsNone(account.account_id)
        self.dal.create(account)
        self.assertIsNotNone(account.account_id)
        self.assertIsInstance(account.account_id, unicode)
        saved = self.dal.try_get(account.email)
        self.account_equals(account, saved)

    def test_create_with_existing_override_previous(self):
        acc_overriden = create_account(u'old_test_create_with_existing_override_previous')
        self.dal.create(acc_overriden)
        acc_new = create_account(u'new_test_create_with_existing_override_previous')
        acc_new.email = acc_overriden.email
        self.dal.create(acc_new)
        result = self.dal.try_get(acc_overriden.email)
        self.account_equals(acc_new, result)

    def test_try_get_with_nothing_return_none(self):
        result = self.dal.try_get(u'test_try_get_with_nothing_return_none')
        self.assertIsNone(result)

    def test_modified(self):
        initial = create_account(u'initial_test_modified')
        self.dal.create(initial)
        modified = create_account(u'modified_test_modified')
        self.dal.modify(initial.account_id, modified)
        initial_result = self.dal.try_get(initial.email)
        self.assertIsNone(initial_result)
        modified_result = self.dal.try_get(modified.email)
        self.account_equals(modified, modified_result)
        self.assertIsNotNone(modified.account_id)
        self.assertEquals(initial.account_id, modified.account_id)

    def test_delete_with_existing(self):
        account = create_account(u'test_delete_with_existing')
        self.dal.create(account)
        self.dal.delete(account.email)
        result = self.dal.try_get(account.email)
        self.assertIsNone(result)

    def test_delete_with_missing_do_not_crash(self):
        self.dal.delete(u'test_delete_with_missing_do_not_crash')

    def account_equals(self, expected, result):
        self.assertEquals(expected.account_id, result.account_id)
        self.assertEquals(expected.email, result.email)
        self.assertEquals(expected.password_hash, result.password_hash)


def create_account(prefix, with_id=False):
    return Account(u'email' + prefix,
                   u'pwd' + prefix,
                   u'id' + prefix if with_id else None)


if __name__ == '__main__':
    unittest.main()
