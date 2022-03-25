""" Users Endpoints """
from flask import request
from flask_jwt_extended import get_jwt_identity, get_raw_jwt
from flask_restx import Namespace, Resource, fields, inputs, reqparse
from service.users import (LoginUser,
                           RefreshTokenService, TokensService,
                           UserLogoutRevokeAccessTokenService,
                           UserLogoutRevokeRefreshTokenService, UserService,
                           )
from util.auth import is_api_protected
from util.jwt_auth import check_apis_are_protected_or_open

JWT_REQUIRED, JWT_REFRESH_TOKEN_REQUIRED = check_apis_are_protected_or_open()


NS = Namespace(
    'users',
    description='NFT user management')

LOGIN_USER = NS.model('LoginUser', {
    'userName': fields.String(
        required=True,
        description='domain and username of the user')
})

user_token_expires_args = reqparse.RequestParser()
user_token_expires_args.add_argument(
    'expires', type=inputs.boolean, required=True,
    help='expires = True for expiry token, expires = False for unexpiry token')



# @NS.route('/<string:userName>')
# class User(Resource):
#     """ User class """
#     @JWT_REQUIRED
#     def get(self, userName):
#         """ Get a user """
#         current_user = get_jwt_identity()
#         return UserService().get_user(userName, current_user)

#     @JWT_REQUIRED
#     def delete(self, userName):
#         """ Delete a user """
#         current_user = get_jwt_identity()
#         return UserService().delete_user(userName, current_user)


@NS.route('/login')
class Login(Resource):
    """ Login class """
    @NS.expect(LOGIN_USER, validate=True)
    def post(self):
        """ Login a user """
        if is_api_protected():
            login_data = request.get_json()
            return LoginUser().login_user(login_data)
        else:
            return {
                "message": "Api is not secured. Login not required"
            }, 200

# @NS.route('/<string:userName>/tokens')
# class Tokens(Resource):
#     """ Class to manage expiry and unexipiry tokens """
#     @NS.doc(parser=user_token_expires_args)
#     @JWT_REQUIRED
#     def put(self, userName):
#         """ Manage a User to have expiry or unexipiry tokens """
#         query_params = user_token_expires_args.parse_args()
#         current_user = get_jwt_identity()
#         return TokensService().put_user(userName, current_user, query_params)


# @NS.route('/refresh-token')
# class RefreshToken(Resource):
#     """ Class to generate access token from refresh token """
#     @JWT_REFRESH_TOKEN_REQUIRED
#     def put(self):
#         """ Generate access token from refresh token """
#         if is_api_protected():
#             current_user = get_jwt_identity()
#             return RefreshTokenService().get_access_token(current_user)
#         else:
#             return {
#                 "message": "Api is not secured"
#             }, 200


# @NS.route('/revoke-access-token')
# class UserLogoutRevokeAccessToken(Resource):
#     """ Class to revoke access token """
#     @JWT_REQUIRED
#     def put(self):
#         """ Revoke access token """
#         if is_api_protected():
#             jti = get_raw_jwt()['jti']
#             return UserLogoutRevokeAccessTokenService().revoke_access_token(
#                 jti)
#         else:
#             return {
#                 "message": "Api is not secured"
#                 }, 200


# @NS.route('/revoke-refresh-token')
# class UserLogoutRevokeRefreshToken(Resource):
#     """ Class to revoke refresh token """
#     @JWT_REFRESH_TOKEN_REQUIRED
#     def put(self):
#         """ Revoke refresh token """
#         if is_api_protected():
#             jti = get_raw_jwt()['jti']
#             return UserLogoutRevokeRefreshTokenService().revoke_refresh_token(
#                 jti)
#         else:
#             return {
#                 "message": "Api is not secured"
#                 }, 200
