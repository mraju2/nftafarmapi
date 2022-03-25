"""
Handles all database interactions
"""
from pymongo import MongoClient
import urllib.parse
import settings
from settings import BLOCK_DB_NAME


class DBUtil:
    """
    Handles all database interactions
    """
    db_host = settings.DB_HOST
    db_user = settings.DB_USER
    db_password = settings.DB_PASSWORD
    db_port = settings.DB_PORT
    db_auth_mech = 'SCRAM-SHA-1'

    def __init__(self, db_name=BLOCK_DB_NAME):
        self.client = MongoClient(
            self.db_host,
            port=self.db_port,
            username=self.db_user,
            password=self.db_password,
            authMechanism=self.db_auth_mech
        )
        self.db_client = self.client[db_name]

    # def __init__(self, db_name='nft-alley'):
    #     username = urllib.parse.quote_plus(self.db_user)
    #     password = urllib.parse.quote_plus(self.db_password)
    #     self.client = MongoClient(
    #         f'mongodb+srv://{username}:{password}@cluster0.jzsno.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
    #     )
    #     self.db_client = self.client[db_name]

    def get_db(self):
        """
        Returns a database client
        """
        return self.db_client

    def get_collection(self, collection_name):
        """ Returns collection """
        return self.db_client[collection_name]

    def query(self, collection_name, query=None, fields=None):
        """ Query data in collection """
        query = query if query else {}
        items = list(
            self.get_collection(
                collection_name
            ).find(query, fields))
        return {
            'items': items
        }, 200
