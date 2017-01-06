import datetime
import jwt
from common.datehelper import utcnow


class Authentication(object):

    def __init__(self, secret_key):
        self._secret_key = secret_key

    def get_token(self, user_id):
        payload = {
            'sub': user_id,
            'iat': utcnow(),
            'exp': utcnow() + datetime.timedelta(days=1)
        }
        token = jwt.encode(payload, self._secret_key, algorithm='HS256')
        return token  # to check, get unicode ?
        # return token.decode('unicode_escape')

    def is_valid(token):
        pass

    def get_user_id(token):
