#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.tools import appengine_rpc_httplib2

def initialize_remote_api():
    auth2 = appengine_rpc_httplib2.HttpRpcServerOAuth2.OAuth2Parameters(
        access_token=None,
        client_id=None,
        client_secret=None,
        scope=None,
        refresh_token=None,
        credential_file=None,
        credentials=None)

    remote_api_stub.ConfigureRemoteApiForOAuth(
        'localhost:33001', '/_ah/remote_api', oauth2_parameters=auth2, secure=False)
