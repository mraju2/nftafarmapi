""" Subscription Endpoint """
from typing import Pattern
from flask import request
from flask_restx import Namespace, Resource, fields

from service.subscription import Subscription
from util.jwt_auth import check_apis_are_protected_or_open
from util.utils import load_json_schema

JWT_REQUIRED, JWT_REFRESH_TOKEN_REQUIRED = check_apis_are_protected_or_open()

NS = Namespace(
    'subscription',
    description='Operations related to configs')

SUBSCRIPTION_MODEL = NS.model('Subscription', 
                {
                    'email': fields.String(
                        required=True,
                        pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                        description='email for subscription'
                    )
                })

@NS.route('/')
class SubscriptionCollection(Resource):
    """ Subscription Collection methods """
    def get(self):
        """ Return list of configs """
        return Subscription().get_all()

    @NS.expect(SUBSCRIPTION_MODEL, validate=True)
    @JWT_REQUIRED
    def post(self):
        """ Creates a config """
        return Subscription().create_one(request.json)


@NS.route('/<string:email>')
class ConfigItem(Resource):
    """ Config Item methods """
    def get(self, email):
        """ Get a config """
        return Subscription().get_one(email)

    # @JWT_REQUIRED
    # def delete(self, configId):
    #     """ Delete a config """
    #     return Config().delete_one(configId)

    # @NS.expect(CONFIG_MODEL, validate=True)
    # @JWT_REQUIRED
    # def put(self, configId):
    #     """ Update a config """
    #     return Config().update_one(configId, request.json)
