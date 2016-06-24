from flask import Blueprint, render_template, redirect, session, request
from dal import Dal, REF_FEATURE_SET  # pylint: disable=relative-import
import frontendstructs as struct  # pylint: disable=relative-import
import passwordhelpers  # pylint: disable=relative-import


# keep low case name because it seems flask / blueprint standard
handlers = Blueprint('handlers', __name__)  # pylint: disable=invalid-name

DAL = Dal()


class Link(object):

    def __init__(self, key, text):
        self.key = key
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
    print "TRACE login()"
    if request.method == 'POST':
        print "TRACE login()::POST"
        email = request.form['email']
        password = request.form['password']

        (user, user_password) = DAL.get_user_and_password(email)
        print "TRACE login()::POST::get_user_and_password"
        if user is not None and passwordhelpers.is_password_valid_for_user(user_password, password):
            set_connected_user(user)
            print "TRACE login()::POST::get_user_and_password::before_redirect"
            return redirect('/')
        else:
            print "TRACE login()::POST::get_user_and_password::before_render_template_login"
            return render_template('login.html', error_message='Unknown email or invalid password')
    else:
        print "TRACE login()::GET::get_connected_user"
        user = get_connected_user()
        if user is None:
            print "TRACE login()::GET::render_template"
            return render_template('login.html')
        else:
            print "TRACE login()::GET::redirect"
            return redirect('/')


@handlers.route('/')
def home():
    print "TRACE home()::start"
    user = get_connected_user()
    if user is not None:
        print "TRACE home()::get_user_docs"
        user_docs = DAL.get_user_docs(user)
        print "TRACE home()::get_user_docs_after"
        links = [Link(key=user_doc.document.key_urlsafe, text=user_doc.document.title) for user_doc in user_docs]
        actions_mapping = {'click_link': struct.UserActionTypeOnDoc.click_link,
                           'up_vote': struct.UserActionTypeOnDoc.up_vote,
                           'down_vote': struct.UserActionTypeOnDoc.down_vote}
        print "TRACE home()::render_template"
        return render_template('index.html', email=user.email, links=links, actions_mapping=actions_mapping)
    else:
        print "TRACE home()::redirect/login"
        return redirect('/login')


@handlers.route('/register', methods=['GET', 'POST'])
def register():
    print "TRACE register()::start"
    if request.method == 'POST':
        print "TRACE register()::POST"
        connected_user = get_connected_user()
        print "TRACE register()::get_connected_user"
        if connected_user is None:
            print "TRACE register()::connected_user None"
            email = request.form['email']
            password = request.form['password']
            interests = request.form['interests'].splitlines()
            print "TRACE register()::before get_user"
            user = DAL.get_user(email)
            print "TRACE register()::after get_user"
            if user is None:
                print "TRACE register()::user is None"
                user = struct.User.make_from_scratch(email, interests)
                DAL.save_user(user, passwordhelpers.hash_password(password))
                print "TRACE register()::save_user"
                # Create an empty profile for the newly created user
                features_set = DAL.get_features(REF_FEATURE_SET)
                print "TRACE register()::get_features"
                feature_vector = struct.FeatureVector.make_from_scratch([1] * len(features_set), REF_FEATURE_SET)
                model_data = struct.UserProfileModelData.make_empty(len(features_set))
                profile = struct.UserComputedProfile.make_from_scratch(feature_vector, model_data)

                DAL.save_computed_user_profiles([(user, profile)])
                print "TRACE register()::save_computed_user_profiles before redirect"
                return redirect('/login')
            else:
                print "TRACE register()::render_template user not None"
                return render_template('register.html', error_message='This account already exists')
        else:
            print "TRACE register()::redirect connected_user is not None"
            return redirect('/')
    else:
        print "TRACE register()::GET"
        user = get_connected_user()
        if user is None:
            print "TRACE register()::GET get_connected_user is None"
            return render_template('register.html')
        else:
            print "TRACE register()::GET/redirect get_connected_user is not None"
            return redirect('/')


@handlers.route('/disconnect')
def disconnect():
    print "TRACE disconnect()::start"
    user = get_connected_user()
    if user is not None:
        print "TRACE disconnect()::user is not None"
        unset_connected_user()
        print "TRACE disconnect()::unset_connected_user"
    print "TRACE disconnect()::redirect/login"
    return redirect('/login')


@handlers.route('/link/<int:action_type_on_doc>/<document_key>')
def link(action_type_on_doc, document_key):
    print "TRACE link()::start"
    user = get_connected_user()
    print "TRACE link()::get_connected_user"
    if user is not None:
        print "TRACE link()::get_connected_user user is not None"
        document = DAL.get_doc_by_urlsafe_key(document_key)
        print "TRACE link()::save_user_action_on_doc"
        DAL.save_user_action_on_doc(user, document, action_type_on_doc)
        print "TRACE link()::before action_type_on_doc"
        if action_type_on_doc == struct.UserActionTypeOnDoc.click_link:
            print "TRACE link()::click_link"
            return redirect(document.url.encode('utf-8'))
        else:
            print "TRACE link():: else click_link"
            return redirect('/')
    else:
        print "TRACE link():: else user is none redirect login"
        return redirect('/login')
