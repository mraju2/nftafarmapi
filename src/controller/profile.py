""" Profiles Endpoint """
from flask import request
from flask_restx import Namespace, Resource, fields, inputs, reqparse

from service.profile import Profile
from util.jwt_auth import check_apis_are_protected_or_open
from util.utils import load_json_schema
from service.profile_follows import ProfileFollows

JWT_REQUIRED, JWT_REFRESH_TOKEN_REQUIRED = check_apis_are_protected_or_open()

NS = Namespace(
    'profiles',
    description='Operations related to profiles')

PROFILE_MODEL = NS.schema_model('Profile', load_json_schema('user-schema.json'))
PROFILE_EDIT_MODEL=NS.schema_model("ProfileEdit",load_json_schema('profile-edit-schema.json'))
VERIFIED_MODEL=NS.model('Verified',{
    'address':fields.String(
        required=True,
        descrption="wallet address"
    ),
    'verified':fields.Boolean(
        required=True,
        descrption=" verified or not "
    ),
    'sign':fields.String(
        required=False,
        descrption="Signature of user"
    )
})

ASSET_FOLLOW_MODEL = NS.model('ProfileFollows',
            {
                'address': fields.String(
                    required=True,
                    descrption="address of w"
                ),
                'followingAddress':fields.String(
                    required=True,
                    description="following address"
                ),
                'follow':fields.Boolean(
                    required=True,
                    description="following status"
                ),
                'sign':fields.String(
                    required=True,
                    description="Sign for Following"
                )
            }
        )

PARSER = reqparse.RequestParser()
PARSER.add_argument(
    'verified', type=inputs.boolean, required=False,
    help='Get profile with verified'
)
PARSER.add_argument(
    'limit', type=str, required=False,
    help='Limit for assets'
)
PARSER.add_argument(
    'offset', type=str, required=False,
    help='Offset for assets'
)

@NS.route('/')
class ProfileCollection(Resource):
    """ Profiles Collection methods """
    @NS.doc(parser=PARSER)
    def get(self):
        """ Return list of profiles """
        args = PARSER.parse_args()
        verified= args.get('verified', None)
        print(verified)
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        return Profile().get_all(verified=verified, limit=limit, offset=offset)

    @NS.expect(PROFILE_MODEL, validate=True)
    @JWT_REQUIRED
    def post(self):
        """ Creates a profile """
        return Profile().create_one(request.json)


@NS.route('/<string:address>')
class ProfileItem(Resource):
    """ Profile Item methods """
    def get(self, address):
        """ Get a profile """
        return Profile().get_one(address)

    # @JWT_REQUIRED
    # def delete(self, address):
    #     """ Delete a profile """
    #     return Profile().delete_one(address)

    @NS.expect(PROFILE_EDIT_MODEL, validate=True)
    @JWT_REQUIRED
    def put(self, address):
        """ Update a profile """
        return Profile().update_profile(address, request.json)

@NS.route('/verified')
class VerifiedProfiles(Resource):
    """ Verified Profile Methods """
    @NS.expect(VERIFIED_MODEL,validate=True)
    def post(self):
        """ Verified  Profile """
        return Profile().verify_profile(request.json) 



@NS.route('/follows')
class ProfileFollowsCollection(Resource):
    """ Post Profile Follow methods """
    @NS.expect(ASSET_FOLLOW_MODEL, validate=True)
    @JWT_REQUIRED
    def post(self):
        """ Creates a like for asset """
        return ProfileFollows().update_follow(request.json)


@NS.route('/follows/<string:address>')
class ProfileFollowsItem(Resource):
    """ profile follows for Item methods """
    def get(self, address):
        """ Get follow for profile """
        return ProfileFollows().get_one(address)

@NS.route('/followedby/<string:address>')
class ProfileFollowedByItem(Resource):
    """ Get profile for followed methods """
    def get(self, address):
        """ Get liked assets for user """
        return ProfileFollows().get_following_profiles(address)



        
