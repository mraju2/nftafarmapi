""" Module handles common database functionality """
import os
from datetime import datetime
from settings import USE_MONGO
from util.db_util import DBUtil

CLIENT = DBUtil(db_name='nft-alley-users').get_db()
USERS = CLIENT['users']
REVOKED_TOKEN = CLIENT['revoked_token']


def get_admin_users():
    """ Method to get all admin uses """
    admin_users = list(USERS.find({"admin": True}))
    return admin_users

def get_current_user(current_user):
    """ Method to verify is incoming JWT is valid """
    users = USERS.find_one({"userName": current_user})
    return users

def is_admin(current_user):
    """ Method to verify if JWT user identity is admin """
    user_admin_check = USERS.find_one({"userName": current_user,
                                    "admin": True})
    return user_admin_check


def is_api_protected():
    """ Method to verify if api is protected or not """
    api_unprotected = os.environ.get('API_UNPROTECTED', "FALSE").upper()
    if api_unprotected == "TRUE":
        return False
    return True


def insert_a_record(userName, admin, token_expires,
                    current_user=None):
    """ Method to create a user """
    USERS.insert_one({'userName': userName,
                    'admin': admin,
                    'token_expires': token_expires,
                    'created_on': datetime.utcnow(),
                    'created_by': current_user})


def update_a_record(userName, token_expires, current_user=None):
    """ Method to update a user """
    myquery = {"userName": userName}
    newvalues = {"$set": {"token_expires": token_expires,
                        "updated_on": datetime.utcnow(),
                        "updated_by": current_user}}
    USERS.update_one(myquery, newvalues)


def update_user_to_admin(userName, current_user=None):
    """ Method to update a user to admin """
    myquery = {"userName": userName}
    newvalues = {"$set": {"admin": True,
                        "updated_on": datetime.utcnow(),
                        "updated_by": current_user}}
    USERS.update_one(myquery, newvalues)


def delete_a_record(userName):
    """ Method to delete a user """
    myquery = {"userName": userName}
    USERS.delete_one(myquery)
