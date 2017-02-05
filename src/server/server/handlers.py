# -*- coding: utf-8 -*-
import logging
from flask import Blueprint, render_template, redirect, session, request
import common.crypto as crypto
from userdocmatch.api import UserDocMatcher, ActionTypeOnDoc
from .dalaccount import DalAccount, Account

# keep low case name because it seems flask / blueprint standard
handlers = Blueprint('handlers', __name__, template_folder='templates')  # pylint: disable=invalid-name
LOGGER = logging.getLogger(__name__)
USER_DOC_MATCHER = UserDocMatcher()


def get_dal_account():
    return DalAccount()


class Link(object):

    def __init__(self, url_hash, text):
        self.url_hash = url_hash
        self.text = text


def set_connected_user(user_id, email):
    session['user_id'] = user_id
    session['email'] = email


def unset_connected_user():
    session.pop('user_id', None)
    session.pop('email', None)


def get_connected_user_id():
    return session.get('user_id')


def get_connected_user_email():
    return session.get('email')


@handlers.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        account = get_dal_account().try_get(email)
        if account is not None and crypto.verify_password(password, account.password_hash):
            set_connected_user(account.account_id, email)
            return redirect('/')
        else:
            return render_template('login.html', error_message='Unknown email or invalid password')
    else:
        user_id = get_connected_user_id()
        if user_id is None:
            return render_template('login.html')
        else:
            return redirect('/')


@handlers.route('/')
def home():
    user_id = get_connected_user_id()
    if user_id is not None:
        docs = USER_DOC_MATCHER.get_docs(user_id)
        links = [Link(url_hash=doc.url_hash, text=doc.title) for doc in docs]
        actions_mapping = {'click_link': ActionTypeOnDoc.click_link,
                           'up_vote': ActionTypeOnDoc.up_vote,
                           'down_vote': ActionTypeOnDoc.down_vote}

        # renamed to index_legacy to not interfere with generated react index.html
        # http://stackoverflow.com/questions/22190881/flask-multiple-blueprints-interfere-with-each-other
        return render_template(
            'index_legacy.html', email=get_connected_user_email(), links=links, actions_mapping=actions_mapping)
    else:
        return redirect('/login')


@handlers.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = get_connected_user_id()
        if user_id is None:
            email = request.form['email']
            password = request.form['password']
            interests = request.form['interests'].splitlines()
            dal_account = get_dal_account()
            if not dal_account.exists(email):
                account = Account(email, crypto.hash_password(password))
                dal_account.create(account)
                user_id = account.account_id
                USER_DOC_MATCHER.create_user(user_id, interests)
                LOGGER.info('new user created, email {%s}', email)
                set_connected_user(user_id, email)
                return redirect('/')
            else:
                return render_template('register.html', error_message='This account already exists')
        else:
            return redirect('/')
    else:
        user_id = get_connected_user_id()
        if user_id is None:
            return render_template('register.html')
        else:
            return redirect('/')


@handlers.route('/disconnect')
def disconnect():
    user_id = get_connected_user_id()
    if user_id is not None:
        unset_connected_user()
    return redirect('/login')


@handlers.route('/link/<int:action_type_on_doc>/<url_hash>')
def link(action_type_on_doc, url_hash):
    user_id = get_connected_user_id()
    if user_id is not None:
        url = USER_DOC_MATCHER.get_url(url_hash)
        USER_DOC_MATCHER.add_user_action(user_id, url_hash, action_type_on_doc)
        if action_type_on_doc == ActionTypeOnDoc.click_link:
            return redirect(url.encode('utf-8'))
        else:
            return redirect('/')
    else:
        return redirect('/login')


@handlers.errorhandler(404)
def page_not_found(exception):
    LOGGER.exception('Error 404')
    unset_connected_user()
    return str(exception)


@handlers.errorhandler(500)
def internal_server_error(exception):
    LOGGER.exception('Error 500')
    unset_connected_user()
    return str(exception)


@handlers.errorhandler(Exception)
def unhandled_exception(exception):
    LOGGER.exception('Error exception')
    unset_connected_user()
    return str(exception)
