"""
User Management
"""
import json
import logging
from datetime import timedelta
from bson import json_util
from flask_jwt_extended import create_access_token, create_refresh_token
from passlib.hash import pbkdf2_sha256 as sha256
from util.auth import (REVOKED_TOKEN, USERS, delete_a_record, get_admin_users,
                       get_current_user, insert_a_record, is_admin,
                       is_api_protected, update_a_record, update_user_to_admin)
from settings import TOKEN_EXPIRATION_TIME, USE_MONGO

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


class UserService:
    """ User class """
    @staticmethod
    def get_user(userName, current_user):
        """ Get User """
        try:
            LOGGER.info("Fetching the user '%s' details", userName)
            if is_api_protected():
                user_valid_check = get_current_user(current_user)
                if not user_valid_check:
                    return {'error': 'Authenticated user "{}" not'
                                     ' a valid user'.format(current_user)}, 403
            db_user_data = get_current_user(userName)
            if not db_user_data:
                message = {
                    "message": "User '{}' does not"
                               " exist".format(userName)
                }
                response_code = 404
                return message, response_code
            message = {
                "message": json.loads(json_util.dumps(db_user_data))
            }
            response_code = 200
        except Exception as ex:  # pylint: disable=broad-except
            message = "Error occured in fetching"\
                " User '{}' details: {}".format(userName, ex)
            response_code = 400
            LOGGER.error(message)
        return message, response_code

    def put_user(userName, current_user=None):
        """ Promote User as admin """
        try:
            if is_api_protected():
                user_valid_check = get_current_user(current_user)
                user_admin_check = is_admin(current_user)
                if not user_valid_check['userName']:
                    return {'error': 'Authenticated user "{}" not'
                                     ' a valid user'.format(current_user)}, 403
                if not user_admin_check['userName']:
                    message = "Admin privileges are required to "\
                              "promote a user to admin"
                    response_code = 403
                    return message, response_code
            db_user_data = get_current_user(userName)
            user_payload_admin_check = is_admin(userName)
            if not db_user_data['userName']:
                message = {
                    "message": "User '{}' does not exist".format(userName)
                }
                response_code = 404
                return message, response_code
            if user_payload_admin_check:
                message = "User '{}' already admin".format(userName)
                response_code = 409
            else:
                update_user_to_admin(userName, current_user)
                message = 'User "{}" promoted to admin'.format(userName)
                response_code = 200
        except Exception as ex:  # pylint: disable=broad-except
            message = "Error occured in promoting"\
                " user '{}' as admin: {}".format(userName, ex)
            response_code = 400
        return message, response_code


class TokensService:
    """ Promote User to have unexpiry token"""
    @staticmethod
    def put_user(userName, current_user, query_params):
        """ Method to update user with token_expires = False """
        try:
            expires = query_params.get('expires', None)
            if expires is None:
                raise KeyError
            if not isinstance(expires, bool):
                message = {
                    "message": "[QUERY PARAMETER] 'expires' should"
                               " be boolean <true or false>"
                }
                response_code = 400
                return message, response_code
            db_user_data = get_current_user(userName)
            if not db_user_data:
                message = {
                    "message": "User '{}' does not exist".format(userName)
                }
                response_code = 404
                return message, response_code
            if expires:
                token_expires = True
                message = 'User "{}" updated to'\
                    ' have an expiry token'.format(userName)
            else:
                token_expires = False
                message = 'User "{}" updated to'\
                    ' have an unexpiry token'.format(userName)
            if is_api_protected():
                user_valid_check = get_current_user(current_user)
                user_admin_check = is_admin(current_user)
                if not user_valid_check:
                    return {'error': 'Authenticated user "{}" not'
                                     ' a valid user'.format(current_user)}, 403
                if not user_admin_check:
                    message = "Admin privileges are required to "\
                              "promote a user to admin"
                    response_code = 403
                    return message, response_code
                if user_admin_check or current_user == userName:
                    update_a_record(userName, token_expires, current_user)
                    response_code = 201
            else:
                update_a_record(userName, token_expires)
                response_code = 201
        except KeyError as k_e:  # pylint: disable=broad-except
            message = {
                "message": "Key 'expires' not found in"
                           " query parameters: {}".format(k_e)
            }
            response_code = 400
        except Exception as ex:  # pylint: disable=broad-except
            message = "Error occured in updating user to"\
                " have unexpiry token: {}".format(ex)
            response_code = 400
        return message, response_code


class RefreshTokenService:
    """ Refresh token class """
    @staticmethod
    def get_access_token(current_user):
        """ Method to refresh access token """
        try:
            access_token = create_access_token(identity=current_user)
            message = {
                'username': current_user,
                'message': 'Access token has been generated',
                'access_token': access_token
            }
            response_code = 200
        except Exception as ex:  # pylint: disable=broad-except
            message = {
                "message": "Error occured in creating"
                           " access token: {}".format(ex)
            }
            response_code = 400
        return message, response_code


class RevokeAccessRefreshTokens:
    """ Manages Access and Refresh tokens """
    def __init__(self, jti):
        self.jti = jti

    def post(self):
        """ Revokes tokens after user logout """
        REVOKED_TOKEN.insert({'token': self.jti})

    def get(self):
        """ Returns blacklisted tokens """
        return REVOKED_TOKEN.find_one({'token': self.jti})


class UserLogoutRevokeAccessTokenService:
    """ Revokes access token """
    @staticmethod
    def revoke_access_token(jti):
        """ Method to revoke access token """
        try:
            revoke_token = RevokeAccessRefreshTokens(jti)
            revoke_token.post()
            message = {
                'message': 'Access token has been revoked'
            }
            response_code = 200
        except Exception as ex:  # pylint: disable=broad-except
            message = {
                'message': 'Something went wrong: {}'.format(ex)
            }
            response_code = 400
        return message, response_code


class UserLogoutRevokeRefreshTokenService:
    """ Revokes refresh token """
    @staticmethod
    def revoke_refresh_token(jti):
        """ Method to revoke access token """
        try:
            revoke_token = RevokeAccessRefreshTokens(jti)
            revoke_token.post()
            message = {
                'message': 'Refresh token has been revoked',
                }
            response_code = 200
        except Exception as ex:  # pylint: disable=broad-except
            message = {
                'message': 'Something went wrong: {}'.format(ex),
                }
            response_code = 400
        return message, response_code
        

class LoginUser:
    """ User login class """
    @staticmethod
    def login_user(user_auth):
        """ Method to verify User is authenticated """
        try:
            # auth_resp = LDAP().is_authenticated(user_auth)
            auth_resp = 'ASSET'
            if isinstance(auth_resp, int):
                LOGGER.error('Invalid username or password.')
                return {
                    'error': 'Invalid username or password.'
                }, 401
            if auth_resp:
                role = []
                if isinstance(auth_resp, list):
                    role = auth_resp
                    auth_resp = 'VISUALIZATION'
                message = {
                    "message": "Generating access and refresh tokens"
                               " for the User '{}'".format(user_auth['userName'])
                }
                login_user = get_current_user(user_auth['userName'])
                if not login_user:
                    insert_a_record(user_auth['userName'],
                                    True, True,
                                    user_auth['userName'])
                    login_user = get_current_user(user_auth['userName'])
                token_expires = login_user.get('token_expires', None)
                token_identity = {
                    'userName': login_user['userName'],
                    'role': auth_resp
                }
                if token_expires is True or token_expires is None:
                    if token_expires is None:
                        update_a_record(login_user['userName'], True,
                                        current_user=login_user['userName'])
                    expires = timedelta(hours=int(TOKEN_EXPIRATION_TIME))
                    access_token = create_access_token(
                        identity=token_identity,
                        expires_delta=expires
                        )
                    refresh_token = create_refresh_token(
                        identity=token_identity,
                        expires_delta=expires
                        )
                else:
                    access_token = create_access_token(
                        identity=token_identity,
                        expires_delta=False
                        )
                    refresh_token = create_refresh_token(
                        identity=token_identity,
                        expires_delta=False
                        )
                message = {
                    'message': 'Logged in as {}'.format(login_user[
                        'userName']),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
                response_code = 200
            else:
                LOGGER.error('Access denied.')
                message = {
                    "message": "Access denied."
                    
                }
                response_code = 403
        except Exception as ex:  # pylint: disable=broad-except
            message = {
                "message": "Error occured in user login: {}".format(ex)
            }
            response_code = 400
        return message, response_code
