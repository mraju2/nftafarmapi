""" collection Endpoint """
from flask import request
from flask_restx import Namespace, Resource, fields, inputs, reqparse
from service.collections import Collection
from util.jwt_auth import check_apis_are_protected_or_open
from util.utils import load_json_schema

JWT_REQUIRED, JWT_REFRESH_TOKEN_REQUIRED = check_apis_are_protected_or_open()

NS = Namespace(
    'collections',
    description='Operations related to collections')

COLLECTION_MODEL = NS.schema_model('Collections', load_json_schema('collections-schema.json'))
COLLECTION_EDIT_MODEL=NS.schema_model("CollectionsEdit",load_json_schema('collections-edit-schema.json'))



PARSER = reqparse.RequestParser()
PARSER.add_argument(
    'creatorId', type=str, required=False,
    help='Get collections by creatorId'
)
PARSER.add_argument(
    'limit', type=str, required=False,
    help='Limit for collections'
)
PARSER.add_argument(
    'offset', type=str, required=False,
    help='Offset for collections'
)

@NS.route('/')
class CollectionsCollection(Resource):
    """ Collections Collection methods """
    @NS.doc(parser=PARSER)
    def get(self):
        """ Return list of collections """
        args = PARSER.parse_args()
        creatorId= args.get('creatorId', None)
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        return Collection().get_all(creatorId=creatorId, limit=limit, offset=offset)

    @NS.expect(COLLECTION_MODEL, validate=True)
    def post(self):
        """ Creates a collections """
        return Collection().create_one(request.json)


@NS.route('/<string:Id>')
class CollectionsItem(Resource):
    """ Collections Item methods """
    def get(self, Id):
        """ Get a collection """
        return Collection().get_one_by_collectionId(Id)

    # @JWT_REQUIRED
    # def delete(self, address):
    #     """ Delete a profile """
    #     return Profile().delete_one(address)

    @NS.expect(COLLECTION_EDIT_MODEL, validate=True)
    @JWT_REQUIRED
    def put(self,Id):
        """ Update a Collection """
        return Collection().update_one(Id, request.json)
    def delete(self,Id):
        """ Delete a Collection """
        return Collection().delete_one(Id)    



        
