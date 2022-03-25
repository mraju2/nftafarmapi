""" Module holds JWT authentication """
from settings import API_UNPROTECTED


# pylint: disable=unused-import, import-outside-toplevel
def check_apis_are_protected_or_open():
    """ Method to check whether the apis are open or protected """
    if API_UNPROTECTED.upper() == "TRUE":
        def jwt_required(func):
            """ Decorator just returns the function if
            no environment variable found """
            return func

        def jwt_refresh_token_required(func):
            """ Decorator just returns the function if
            no environment variable found """
            return func
    else:
        from flask_jwt_extended import jwt_required, jwt_refresh_token_required
    return jwt_required, jwt_refresh_token_required
