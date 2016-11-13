import unittest
from common.crypto import hash_password, hash_str, verify_password


class CryptoTests(unittest.TestCase):

    def test_hash_str_return_unicode(self):
        message_to_hash = u'test_hash_str_return_unicode'
        hashed = hash_str(message_to_hash)
        self.assertIsInstance(hashed, unicode)

    def test_hash_str_same_str_return_same_hash(self):
        message_to_hash = u'test_hash_str_same_str_return_same_hash'
        hash_1 = hash_str(message_to_hash)
        hash_2 = hash_str(message_to_hash)
        self.assertEquals(hash_1, hash_2)

    def test_hash_str_diff_str_return_diff_hash(self):
        message_to_hash = u'test_hash_str_diff_str_return_diff_hash'
        hash_1 = hash_str(message_to_hash)
        hash_2 = hash_str(message_to_hash + '0')
        self.assertNotEquals(hash_1, hash_2)

    def test_hash_password_return_unicode(self):
        message_to_hash = u'test_hash_password_return_unicode'
        hashed = hash_password(message_to_hash)
        self.assertIsInstance(hashed, unicode)

    def test_hash_verify_password_right_password_return_true(self):
        message_to_hash = u'test_hash_verify_password_right_password_return_true'
        hashed = hash_password(message_to_hash)
        password_ok = verify_password(message_to_hash, hashed)
        self.assertTrue(password_ok)

    def test_hash_verify_password_wrong_password_return_false(self):
        message_to_hash = u'test_hash_verify_password_wrong_password_return_false'
        hashed = hash_password(message_to_hash)
        password_ok = verify_password(message_to_hash + '0', hashed)
        self.assertFalse(password_ok)

    def test_hash_password_two_times_return_different_hash(self):
        message_to_hash = u'test_hash_password_two_times_return_different_hash'
        hash_1 = hash_password(message_to_hash)
        hash_2 = hash_password(message_to_hash)
        self.assertNotEquals(hash_1, hash_2)


if __name__ == '__main__':
    unittest.main()
