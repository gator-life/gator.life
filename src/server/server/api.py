# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restful import Api, Resource

api_blueprint = Blueprint('api', __name__, template_folder='.')  # pylint: disable=invalid-name
api = Api(api_blueprint)  # pylint: disable=invalid-name


@api.resource('/api/user/<string:user_email>')
class UserAPI(Resource):

    @staticmethod
    def get(user_email):
        return {'email': 'test_API ' + user_email}
