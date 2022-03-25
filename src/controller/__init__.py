""" Controller __init__.py """
from flask_restx import Api
from flask import url_for

from .asset import NS as asset_ns
from .asset_archived import NS as asset_archived_ns
from .config import NS as config_ns
from .profile import NS as profile_ns
from .transaction import NS as transaction_ns
from .offer import NS as offer_ns
from .users import NS as users_ns 
from .report import NS as report_ns
from .subscription import NS as subscription_ns
from .reportnft_delist import NS as reportnft_delist_ns
from .collections import NS as collections_ns


AUTHORIZATIONS = {
            'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    }


class Custom_API(Api):
    @property
    def specs_url(self):
        '''
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        '''
        return url_for(self.endpoint('specs'), _external=False)


API = Custom_API(
    version='0.1.0',
    title='NFT Alley API',
    description='REST API for NFT Alley',
    security='Bearer Auth',
    authorizations=AUTHORIZATIONS)

API.add_namespace(asset_ns)
API.add_namespace(asset_archived_ns)
API.add_namespace(config_ns)
API.add_namespace(offer_ns)
API.add_namespace(profile_ns)
API.add_namespace(report_ns)
API.add_namespace(subscription_ns)
API.add_namespace(transaction_ns)
API.add_namespace(users_ns)
API.add_namespace(reportnft_delist_ns)
API.add_namespace(collections_ns)
