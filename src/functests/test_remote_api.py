import unittest
from common.remote_api import initialize_remote_api
import daltesthelpers as daltesthelpers
import server.dal as dal


class RemoteAPiTests(unittest.TestCase):

    def test_save_then_data_with_remote_api(self):
        initialize_remote_api()

        daltesthelpers.create_user_dummy('test_save_then_data_with_remote_api', 'password', ['interests'])
        user = dal.get_user('test_save_then_data_with_remote_api')
        self.assertEquals('test_save_then_data_with_remote_api', user.email)


if __name__ == '__main__':
    unittest.main()
