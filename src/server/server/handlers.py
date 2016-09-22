# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, session, request
from .dal import Dal, REF_FEATURE_SET
from . import frontendstructs as struct
from . import passwordhelpers


# keep low case name because it seems flask / blueprint standard
handlers = Blueprint('handlers', __name__, template_folder='templates')  # pylint: disable=invalid-name

DAL = Dal()


class Link(object):

    def __init__(self, url_hash, text):
        self.url_hash = url_hash
        self.text = text


def set_connected_user(user):
    session['email'] = user.email


def unset_connected_user():
    session.pop('email', None)


def get_connected_user():
    if 'email' in session:
        return DAL.get_user(session['email'])
    return None


@handlers.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        (user, user_password) = DAL.get_user_and_password(email)
        if user is not None and passwordhelpers.is_password_valid_for_user(user_password, password):
            set_connected_user(user)
            return redirect('/')
        else:
            return render_template('login.html', error_message='Unknown email or invalid password')
    else:
        user = get_connected_user()
        if user is None:
            return render_template('login.html')
        else:
            return redirect('/')


@handlers.route('/')
def home():
    user = get_connected_user()
    if user is not None:
        user_docs = DAL.get_user_docs(user)
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
        connected_user = get_connected_user()
        if connected_user is None:
            email = request.form['email']
            password = request.form['password']
            interests = request.form['interests'].splitlines()

            user = DAL.get_user(email)
            if user is None:
                user = struct.User.make_from_scratch(email, interests)
                DAL.save_user(user, passwordhelpers.hash_password(password))

                # Create an empty profile for the newly created user
                features_set = DAL.get_features(REF_FEATURE_SET)
                feature_vector = struct.FeatureVector.make_from_scratch([1] * len(features_set), REF_FEATURE_SET)
                model_data = struct.UserProfileModelData.make_empty(len(features_set))
                profile = struct.UserComputedProfile.make_from_scratch(feature_vector, model_data)

                DAL.save_user_computed_profiles([(user, profile)])
                set_connected_user(user)
                return redirect('/')
            else:
                return render_template('register.html', error_message='This account already exists')
        else:
            return redirect('/')
    else:
        user = get_connected_user()
        if user is None:
            return render_template('register.html')
        else:
            return redirect('/')


@handlers.route('/disconnect')
def disconnect():
    user = get_connected_user()
    if user is not None:
        unset_connected_user()
    return redirect('/login')


@handlers.route('/link/<int:action_type_on_doc>/<url_hash>')
def link(action_type_on_doc, url_hash):
    user = get_connected_user()
    if user is not None:
        document = DAL.get_doc_by_url_hash(url_hash)
        DAL.save_user_action_on_doc(user, document, action_type_on_doc)
        if action_type_on_doc == struct.UserActionTypeOnDoc.click_link:
            return redirect(document.url.encode('utf-8'))
        else:
            return redirect('/')
    else:
        return redirect('/login')
