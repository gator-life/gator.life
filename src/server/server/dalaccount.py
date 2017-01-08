import google.cloud.datastore as datastore  # pylint: disable=import-error
from .dal import _datastore_test_client, _make_named_entity, _make_entity
from .environment import GCLOUD_PROJECT, IS_TEST_ENV


class Account(object):

    def __init__(self, email, password_hash, account_id=None):
        self.email = email
        self.password_hash = password_hash
        self.account_id = account_id


class DalAccount(object):

    _ds_singleton_test_client = _datastore_test_client() if IS_TEST_ENV else None
    _field_email = 'email'
    _field_pwd = 'password_hash'
    _field_id = 'account_id'
    _entity_account = 'Account'
    _entity_account_key = 'AccountKeyByEmail'

    def __init__(self):
        self._ds_client = self._ds_singleton_test_client if IS_TEST_ENV else datastore.Client(GCLOUD_PROJECT)

    def _account_key(self, account_id_str):
        return self._ds_client.key(self._entity_account, int(account_id_str))

    def _account_key_by_email_key(self, email):
        return self._ds_client.key(self._entity_account_key, email)

    def _to_db_account(self, account):
        not_indexed = (self._field_pwd,)
        db_user = _make_entity(self._ds_client, self._entity_account, not_indexed)
        db_user[self._field_email] = account.email
        db_user[self._field_pwd] = account.password_hash
        if account.account_id is not None:
            db_user.key = self._account_key(account.account_id)
        return db_user

    def _to_account(self, db_account):
        email = db_account[self._field_email]
        password_hash = db_account[self._field_pwd]
        account_id = unicode(db_account.key.id)
        return Account(email, password_hash, account_id)

    def _to_db_account_key_by_email(self, email, account_id):
        db_account_key_by_email = _make_named_entity(self._ds_client, self._entity_account_key, email, [])
        db_account_key_by_email[self._field_id] = account_id
        return db_account_key_by_email

    def _to_account_id_str(self, db_account_key_by_email):
        return unicode(db_account_key_by_email[self._field_id])

    def _delete_account(self, account_id_str):
        account_key = self._account_key(account_id_str)
        self._ds_client.delete(account_key)

    def _delete_account_key_by_email(self, email):
        account_key_by_email_key = self._account_key_by_email_key(email)
        self._ds_client.delete(account_key_by_email_key)

    def _try_get_account_id_str(self, email):
        account_key_by_email_key = self._account_key_by_email_key(email)
        db_account_key_by_email = self._ds_client.get(account_key_by_email_key)
        if db_account_key_by_email is None:
            return None
        account_id = self._to_account_id_str(db_account_key_by_email)
        return account_id

    def _get_by_account_id_str(self, account_id_str):
        db_account_key = self._account_key(account_id_str)
        db_account = self._ds_client.get(db_account_key)
        account = self._to_account(db_account)
        return account

    def exists(self, email):
        email_key = self._account_key_by_email_key(email)
        db_account_key_by_email = self._ds_client.get(email_key)
        return db_account_key_by_email is not None

    def create(self, account):
        db_account = self._to_db_account(account)
        self._ds_client.put(db_account)
        db_account_key_by_email = self._to_db_account_key_by_email(account.email, db_account.key.id)
        self._ds_client.put(db_account_key_by_email)
        account.account_id = unicode(db_account.key.id)

    def modify(self, account_id, new_account):
        old_account = self._get_by_account_id_str(account_id)
        new_account.account_id = account_id
        self.create(new_account)
        if old_account.email != new_account.email:
            self._delete_account_key_by_email(old_account.email)

    def delete(self, email):
        account_id_str = self._try_get_account_id_str(email)
        if account_id_str is not None:
            self._delete_account(account_id_str)
            self._delete_account_key_by_email(email)

    def try_get(self, email):
        account_id_str = self._try_get_account_id_str(email)
        if account_id_str is None:
            return None
        account = self._get_by_account_id_str(account_id_str)
        return account
