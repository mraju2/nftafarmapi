""" Configs Endpoint """
from flask import request
from flask_restx import Namespace, Resource, fields

from service.config import Config
from util.jwt_auth import check_apis_are_protected_or_open
from util.utils import load_json_schema

JWT_REQUIRED, JWT_REFRESH_TOKEN_REQUIRED = check_apis_are_protected_or_open()

NS = Namespace(
    'configs',
    description='Operations related to configs')

CONFIG_MODEL = NS.model('Config', 
                {
                    'name': fields.String(
                        required=True,
                        description='Key for config'
                    ),
                    'value': fields.String(
                        required=True,
                        description='Value for config'
                    ),
                    'token': fields.String(
                        required=True,
                        description='Token for config'
                    )
                })

@NS.route('/')
class ConfigCollection(Resource):
    """ Configs Collection methods """
    def get(self):
        """ Return list of configs """
        return Config().get_all()

    # @NS.expect(CONFIG_MODEL, validate=True)
    # @JWT_REQUIRED
    # def post(self):
    #     """ Creates a config """
    #     return Config().create_one(request.json)


@NS.route('/<string:configId>')
class ConfigItem(Resource):
    """ Config Item methods """
    def get(self, configId):
        """ Get a config """
        return Config().get_one(configId)

    # @JWT_REQUIRED
    # def delete(self, configId):
    #     """ Delete a config """
    #     return Config().delete_one(configId)

    @NS.expect(CONFIG_MODEL, validate=True)
    @JWT_REQUIRED
    def put(self, configId):
        """ Update a config """
        return Config().update_one(configId, request.json)
