""" Assets Endpoint """
from flask import request
from flask_restx import Namespace, Resource, fields, inputs, reqparse
from service.asset_archived import AssetArchived
from util.jwt_auth import check_apis_are_protected_or_open
from util.utils import load_json_schema

JWT_REQUIRED, JWT_REFRESH_TOKEN_REQUIRED = check_apis_are_protected_or_open()

NS = Namespace(
    'assetsArchived',
    description='Operations related to archived assets')


@NS.route('/')
class AssetArchivedCollection(Resource):
    """ Archived Assets Collection methods """
    def get(self):
        """ Return list of archived assets """
        return AssetArchived().get_all()


@NS.route('/<string:assetId>')
class AssetArchivedItem(Resource):
    """ Archived Asset Item methods """
    def get(self, assetId):
        """ Get a archived asset """
        return AssetArchived().get_one(assetId)


@NS.route('/count')
class AssetCountCollection(Resource):
    """ Archived Assets Count Collection methods """
    def get(self):
        """ Return count of archived assets """
        return AssetArchived().get_count()