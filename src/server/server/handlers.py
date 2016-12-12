# -*- coding: utf-8 -*-
import logging
from flask import Blueprint, render_template, redirect, session, request
import common.crypto as crypto
from .dal import Dal
from . import frontendstructs as struct
from .structinit import UserCreator

# keep low case name because it seems flask / blueprint standard
handlers = Blueprint('handlers', __name__, template_folder='templates')  # pylint: disable=invalid-name
LOGGER = logging.getLogger(__name__)
USER_CREATOR = UserCreator()


def get_dal():
    # Indirection to enable mocking
    return Dal()


class Link(object):

    def __init__(self, url_hash, text):
        self.url_hash = url_hash
        self.text = text


def set_connected_user(user):
    session['email'] = user.email


def unset_connected_user():
    session.pop('email', None)


def get_connected_user_email():
    return session.get('email')


def get_connected_user(dal):
    email = get_connected_user_email()
    return dal.user.get_user(email) if email else None


@handlers.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        (user, hashed_password) = get_dal().user.get_user_and_hash_password(email)
        if user is not None and crypto.verify_password(password, hashed_password):
            set_connected_user(user)
            return redirect('/')
        else:
            return render_template('login.html', error_message='Unknown email or invalid password')
    else:
        user = get_connected_user(get_dal())
        if user is None:
            return render_template('login.html')
        else:
            return redirect('/')


@handlers.route('/')
def home():
    dal = get_dal()
    user = get_connected_user(dal)
    if user is not None:
        user_docs = dal.user_doc.get_user_docs(user)
        links = [Link(url_hash=user_doc.document.url_hash, text=user_doc.document.title) for user_doc in user_docs]
        actions_mapping = {'click_link': struct.UserActionTypeOnDoc.click_link,
                           'up_vote': struct.UserActionTypeOnDoc.up_vote,
                           'down_vote': struct.UserActionTypeOnDoc.down_vote}

        return render_template('index.html', email=user.email, links=links, actions_mapping=actions_mapping)
    else:
        return redirect('/login')


@handlers.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = get_connected_user_email()
        if email is None:
            email = request.form['email']
            password = request.form['password']
            interests = request.form['interests'].splitlines()
            dal = get_dal()
            user = dal.user.get_user(email)
            if user is None:
                user = USER_CREATOR.create_user_in_db(email, interests, password, dal)
                LOGGER.info('new user created, email {%s}', email)
                set_connected_user(user)
                return redirect('/')
            else:
                return render_template('register.html', error_message='This account already exists')
        else:
            return redirect('/')
    else:
        user = get_connected_user_email()
        if user is None:
            return render_template('register.html')
        else:
            return redirect('/')


@handlers.route('/disconnect')
def disconnect():
    email = get_connected_user_email()
    if email is not None:
        unset_connected_user()
    return redirect('/login')


@handlers.route('/link/<int:action_type_on_doc>/<url_hash>')
def link(action_type_on_doc, url_hash):
    dal = get_dal()
    user = get_connected_user(dal)
    if user is not None:
        document = dal.doc.get_doc(url_hash)
        dal.user_action.save_user_action_on_doc(user, document, action_type_on_doc)
        if action_type_on_doc == struct.UserActionTypeOnDoc.click_link:
            return redirect(document.url.encode('utf-8'))
        else:
            return redirect('/')
    else:
        return redirect('/login')


@handlers.errorhandler(404)
def page_not_found(exception):
    LOGGER.exception('Error 404')
    return str(exception)


@handlers.errorhandler(500)
def internal_server_error(exception):
    LOGGER.exception('Error 500')
    return str(exception)


@handlers.errorhandler(Exception)
def unhandled_exception(exception):
    LOGGER.exception('Error exception')
    return str(exception)
