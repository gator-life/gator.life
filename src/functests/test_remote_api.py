import unittest


class RemoteAPiTests(unittest.TestCase):

    def test_save_then_data_with_remote_api(self):
        from google.appengine.ext.remote_api import remote_api_stub
        from google.appengine.tools import appengine_rpc_httplib2

        auth2 = appengine_rpc_httplib2.HttpRpcServerOAuth2.OAuth2Parameters(
            access_token=None,
            client_id=None,
            client_secret=None,
            scope=None,
            refresh_token=None,
            credential_file=None,
            credentials=None)

        #TODO we should read 33001 from a environment variable or as input, matches travis.yml
        remote_api_stub.ConfigureRemoteApiForOAuth(
            'localhost:33001', '/_ah/remote_api', oauth2_parameters=auth2, secure=False)

        import server.dal as dal
        dal.init_user_dummy('test_save_then_data_with_remote_api')
        user = dal.get_user('test_save_then_data_with_remote_api')
        self.assertEquals('test_save_then_data_with_remote_api', user.email)


if __name__ == '__main__':
    unittest.main()
