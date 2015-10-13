import webapp2

import dal  # pylint: disable=relative-import
import jinjaenvironment # pylint: disable=relative-import


class Link(object):
    def __init__(self, link, text):
        self.link = link
        self.text = text


class Feature(object):
    def __init__(self, label, value):
        self.label = label
        self.value = value


class LoginPageHandler(webapp2.RequestHandler):
    def get(self):
        response = jinjaenvironment.render_template(html_file='login.html', attributes_dict={})
        self.response.write(response)


class HomePageHandler(webapp2.RequestHandler):

    def _get_or_create_user(self):
        email = self.request.get('email')
        user = dal.get_user(email)
        if user is None:
            dal.init_user_dummy(email)
            user = dal.get_user(email)
        return user

    def _get_or_create_features(self, user):
        source = self.request.get('source')
        if source == 'save_features':
            feature_set_id = self.request.get('feature_set_id')
            labels = dal.get_features(feature_set_id)
            vector = [float(self.request.get(label)) for label in labels]
            user.feature_vector = dal.FeatureVector(vector=vector, labels=labels, feature_set_id=feature_set_id)
            dal.save_user(user)

        feature_vector = user.feature_vector
        if feature_vector is None:
            feature_set_id = dal.REF_FEATURE_SET
            labels = dal.get_features(dal.REF_FEATURE_SET)
            vector = [x * 0.1 for x in range(len(labels))]
            feature_vector = dal.FeatureVector(labels=labels, vector=vector, feature_set_id=feature_set_id)

        return feature_vector

    def post(self):
        user = self._get_or_create_user()
        feature_vector = self._get_or_create_features(user)

        links = [Link(link=user_doc.document.url, text=user_doc.document.title) for user_doc in user.user_docs]
        features = [Feature(label, value) for (label, value) in zip(feature_vector.labels, feature_vector.vector)]

        template_values = {
            'email': user.email,
            'links': links,
            'features': features,
            'feature_set_id':feature_vector.feature_set_id
        }
        response = jinjaenvironment.render_template(html_file='index.html', attributes_dict=template_values)

        self.response.write(response)
