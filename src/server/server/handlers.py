import webapp2
from webapp2_extras import sessions
import dal  # pylint: disable=relative-import
import jinjaenvironment  # pylint: disable=relative-import
import frontendstructs as struct  # pylint: disable=relative-import
import frontendhelpers as helpers  # pylint: disable=relative-import


class Link(object):

    def __init__(self, key, text):
        self.key = key
        self.text = text


# How to use sessions :
# http://stackoverflow.com/questions/14078054/gae-webapp2-session-the-correct-process-of-creating-and-checking-sessions
class BaseHandler(webapp2.RequestHandler):

    sessions_store = None

    def dispatch(self):
        self.sessions_store = sessions.get_store(request=self.request)

        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.sessions_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.sessions_store.get_session()

    def set_connected_user(self, user):
        self.session['email'] = user.email

    def unset_connected_user(self):
        self.session['email'] = None

    def get_connected_user(self):
        email = self.session.get('email')
        if email is not None:
            return dal.get_user(email)
        return None


class LoginHandler(BaseHandler):

    def get(self):
        user = self.get_connected_user()
        if user is None:
            response = jinjaenvironment.render_template(html_file='login.html', attributes_dict={})
            self.response.write(response)
        else:
            self.redirect('/')

    def post(self):
        email = self.request.get('email')
        password = self.request.get('password')

        (user, user_password) = dal.get_user_and_password(email)
        if user is not None and helpers.PasswordHelpers.is_password_valid_for_user(user_password, password):
            self.set_connected_user(user)
            self.redirect('/')
        else:
            template_value = {'error_message': 'Unknown email or invalid password'}
            response = jinjaenvironment.render_template(html_file='login.html', attributes_dict=template_value)
            self.response.write(response)


class RegisterHandler(BaseHandler):

    def get(self):
        user = self.get_connected_user()
        if user is None:
            response = jinjaenvironment.render_template(html_file='register.html', attributes_dict={})
            self.response.write(response)
        else:
            self.redirect('/')

    def post(self):
        connected_user = self.get_connected_user()
        if connected_user is None:
            email = self.request.get('email')
            password = self.request.get('password')
            interests = self.request.get('interests').splitlines()

            user = dal.get_user(email)
            if user is None:
                user = struct.User.make_from_scratch(email, interests)
                dal.save_user(user, helpers.PasswordHelpers.hash_password(password))

                # Create an empty profile for the newly created user
                features_set = dal.get_features(dal.REF_FEATURE_SET)
                feature_vector = struct.FeatureVector.make_from_scratch([1]*len(features_set), dal.REF_FEATURE_SET)
                model_data = struct.UserProfileModelData.make_empty(len(features_set))
                profile = struct.UserComputedProfile.make_from_scratch(feature_vector, model_data)

                dal.save_computed_user_profiles([(user, profile)])

                self.redirect('/login')
            else:
                template_value = {'error_message': 'This account already exists'}
                response = jinjaenvironment.render_template(html_file='register.html', attributes_dict=template_value)
                self.response.write(response)
        else:
            self.redirect('/')


class DisconnectHandler(BaseHandler):

    def get(self):
        user = self.get_connected_user()
        if user is not None:
            self.unset_connected_user()
        self.redirect('/login')


class HomeHandler(BaseHandler):

    def get(self):
        user = self.get_connected_user()
        if user is not None:
            user_docs = dal.get_user_docs(user)
            links = [Link(key=user_doc.document._db_key.urlsafe(), # pylint: disable=protected-access
                          text=user_doc.document.title) for user_doc in user_docs]

            template_values = {
                'email': user.email,
                'links': links
            }

            response = jinjaenvironment.render_template(html_file='index.html', attributes_dict=template_values)

            self.response.write(response)
        else:
            self.redirect('/login')


class LinkHandler(BaseHandler):

    def get(self, action, document_key):
        user = self.get_connected_user()
        if user is not None:
            action_type_on_doc = dal.to_user_action_type_on_doc(action)

            document = dal.get_doc_by_urlsafe_key(document_key)

            dal.save_user_action_on_doc(user, document, action_type_on_doc)

            if action_type_on_doc == struct.UserActionTypeOnDoc.click_link:
                self.redirect(document.url.encode('utf-8'))
            else:
                self.redirect('/')
        else:
            self.redirect('/login')
