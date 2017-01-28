from .dal import Dal
from .structinit import UserCreator
from .frontendstructs import UserActionTypeOnDoc


class UserDocMatcher(object):

    def __init__(self):
        self._user_creator = UserCreator()

    def create_user(self, user_id, interests):
        """
        :param user_id: unicode unique identifier of user in UserDocMatch
        :param interests: list of unicode.
        """
        self._user_creator.create_user_in_db(user_id, interests, Dal())

    @staticmethod
    def get_docs(user_id):
        dal = Dal()
        user = dal.user.get_user(user_id)
        dal_user_docs = dal.user_doc.get_user_docs(user)
        docs = [_to_api_doc(user_doc.document) for user_doc in dal_user_docs]
        return docs

    # Nb: this function should be removed and mapping
    # hash/url kept by the client
    @staticmethod
    def get_url(url_hash):
        dal = Dal()
        return dal.doc.get_doc(url_hash).url

    @staticmethod
    def add_user_action(user_id, url_hash, action_type_on_doc):
        dal = Dal()
        dal_action = _to_dal_action(action_type_on_doc)
        dal.user_action.save_user_action_on_doc(user_id, url_hash, dal_action)


class Document(object):

    def __init__(self, url_hash, url, title, summary):
        self.url_hash = url_hash
        self.url = url
        self.title = title
        self.summary = summary


class ActionTypeOnDoc(object):
    # NB: when we manage dependencies in server, we can reference enum34 and make this class an enum
    up_vote = 1
    down_vote = 2
    click_link = 3
    view_link = 4


def _to_api_doc(dal_doc):
    return Document(dal_doc.url_hash, dal_doc.url, dal_doc.title, dal_doc.summary)


def _to_dal_action(api_action_type_on_doc):
    if api_action_type_on_doc == ActionTypeOnDoc.up_vote:
        return UserActionTypeOnDoc.up_vote
    if api_action_type_on_doc == ActionTypeOnDoc.down_vote:
        return UserActionTypeOnDoc.down_vote
    if api_action_type_on_doc == ActionTypeOnDoc.click_link:
        return UserActionTypeOnDoc.click_link
    if api_action_type_on_doc == ActionTypeOnDoc.view_link:
        return UserActionTypeOnDoc.view_link
