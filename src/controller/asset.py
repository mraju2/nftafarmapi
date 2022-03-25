""" Assets Endpoint """
from flask import request
from flask_restx import Namespace, Resource, fields, inputs, reqparse

from service.asset import Asset
from service.asset_likes import AssetLikes
from service.transaction import Transaction
from service.web3 import Web3Alley
from util.jwt_auth import check_apis_are_protected_or_open
from util.utils import load_json_schema

JWT_REQUIRED, JWT_REFRESH_TOKEN_REQUIRED = check_apis_are_protected_or_open()

NS = Namespace(
    'assets',
    description='Operations related to assets')

ASSET_MODEL = NS.schema_model('Asset', load_json_schema('asset-schema.json'))
ASSET_UPDATE_MODEL=NS.schema_model('AssetUpdate',load_json_schema('asset-update-schema.json'))

ASSET_LIKE_MODEL = NS.schema_model('AssetLikes', load_json_schema('asset-like-schema.json'))

ASSET_VIEW_MODEL = NS.model('AssetViews',
            {
                'assetId': fields.String(
                    required=True,
                    descrption="Asset id"
                )
            }
        )

ASSET_FILTER_MODEL = NS.schema_model('AssetFilters', load_json_schema('asset-filter-schema.json'))

BUY_MODEL = NS.model('Buy',
            {
                'assetId': fields.String(
                    required=True,
                    descrption="Asset id"
                ),
                'hash': fields.String(
                    required=True,
                    descrption="Buy Transaction Hash"
                ),
                'buyer': fields.String(
                    required=True,
                    descrption="Buyer Address"
                )
            }
        )

TRANSFER_MODEL = NS.model('Transfer',
            {
                'assetId': fields.String(
                    required=True,
                    descrption="Asset id"
                ),
                'hash': fields.String(
                    required=True,
                    descrption="Transfer Transaction Hash"
                ),
                'to': fields.String(
                    required=True,
                    descrption="Receiver Address"
                )
            }
        )

MINT_MODEL=NS.schema_model('MintAsset', load_json_schema('mint-schema.json')) 

BURN_MODEL=NS.model('Burn',{
    'assetId':fields.String(
        required=True,
        descrption="Asset Id"
    ),
    'hash': fields.String(
        required=True,
        descrption="Transfer Transaction Hash"
    ),
    "sign":fields.String(
        required=True,
        descrption="Signature of user"
    )
})

LIST_MODEL=NS.model('List',{
    'listed':fields.Boolean(
        required=True,
        descrption="Listed or not"
    ),
    'assetId':fields.String(
        required=True,
        descrption="Asset Id"
    ),
    'sign':fields.String(
        required=True,
        descrption="Signature of user"
    )
})

PARSER = reqparse.RequestParser()
PARSER.add_argument(
    'creator', type=str, required=False,
    help='Get assets with creator'
)
PARSER.add_argument(
    'owner', type=str, required=False,
    help='Get assets with owner'
)
PARSER.add_argument(
    'status', type=str, required=False,
    help='Get assets with status'
)
PARSER.add_argument(
    'limit', type=str, required=False,
    help='Limit for assets'
)
PARSER.add_argument(
    'offset', type=str, required=False,
    help='Offset for assets'
)
PARSER.add_argument(
    'onSale',type=inputs.boolean, required=False,
    help='Get assets with onSale'
)

SEARCH_PARSER = reqparse.RequestParser()
SEARCH_PARSER.add_argument(
    'search_text', type=str, required=False,
    help='Get assets, profiles with search_text'
)
SEARCH_PARSER.add_argument(
    'limit', type=str, required=False,
    help='Limit for assets'
)

FILTER_PARSER = reqparse.RequestParser()
FILTER_PARSER.add_argument(
    'limit', type=str, required=False,
    default='20',
    help='Limit for assets'
)
FILTER_PARSER.add_argument(
    'offset', type=str, required=False,
    default='0',
    help='Offset for assets'
)

COUNT_PARSER = reqparse.RequestParser()
COUNT_PARSER.add_argument(
    'creator', type=str, required=False,
    help='Get assets with creator'
)
COUNT_PARSER.add_argument(
    'owner', type=str, required=False,
    help='Get assets with owner'
)
COUNT_PARSER.add_argument(
    'status', type=str, required=False,
    help='Get assets with status'
)

PARSER_COLLECTION=reqparse.RequestParser()
PARSER_COLLECTION.add_argument(
    'collectionId',type=str,required=True,
    help='Get NFTs which belongs to that collection'
)
PARSER_COLLECTION.add_argument(
    'limit', type=str, required=False,
    default='20',
    help='Limit for assets'
)
PARSER_COLLECTION.add_argument(
    'offset', type=str, required=False,
    default='0',
    help='Offset for assets'
)

@NS.route('/')
class AssetCollection(Resource):
    """ Assets Collection methods """
    @NS.doc(parser=PARSER)
    def get(self):
        """ Return list of assets """
        args = PARSER.parse_args()
        creator= args.get('creator', None)
        owner= args.get('owner', None)
        status = args.get('status', None)
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        onSale= args.get('onSale',None)
        return Asset().get_all(creator=creator, owner=owner, status=status, limit=limit, offset=offset,onSale=onSale)

    @NS.expect(ASSET_MODEL, validate=True)
    @JWT_REQUIRED
    def post(self):
        """ Creates a asset """
        return Asset().create_one(request.json)


@NS.route('/<string:assetId>')
class AssetItem(Resource):
    """ Asset Item methods """
    def get(self, assetId):
        """ Get a asset """
        return Asset().get_one(assetId)

    @NS.expect(ASSET_UPDATE_MODEL, validate=True)
    def put(self,assetId):
        """ Perform update in Asset """
        return Transaction().update_asset(assetId, request.json)


@NS.route('/count')
class AssetCountCollection(Resource):
    """ Assets Count Collection methods """
    @NS.doc(parser=COUNT_PARSER)
    def get(self):
        """ Return count of assets """
        args = COUNT_PARSER.parse_args()
        creator= args.get('creator', None)
        owner= args.get('owner', None)
        status = args.get('status', None)
        return Asset().get_count(creator=creator, owner=owner, status=status)

@NS.route('/search')
class SearchCollection(Resource):
    """ Search methods """
    @NS.doc(parser=SEARCH_PARSER)
    def get(self):
        """ Return list of assets, profiles """
        args = SEARCH_PARSER.parse_args()
        search_text= args.get('search_text', None)
        limit = args.get('limit', None)
        return Asset().search(search_text=search_text, limit=limit)

@NS.route('/likes')
class AssetLikesCollection(Resource):
    """ Post Asset Like methods """
    @NS.expect(ASSET_LIKE_MODEL, validate=True)
    @JWT_REQUIRED
    def post(self):
        """ Creates a like for asset """
        return AssetLikes().update_like(request.json)

@NS.route('/views')
class AssetViewsCollection(Resource):
    """ Post Asset Like methods """
    @NS.expect(ASSET_VIEW_MODEL, validate=True)
    def post(self):
        """ Creates a view for asset """
        return AssetLikes().update_views(request.json)

@NS.route('/likes/<string:assetId>')
class AssetLikesItem(Resource):
    """ Asset likes for Item methods """
    def get(self, assetId):
        """ Get like for asset """
        return AssetLikes().get_one(assetId)

@NS.route('/likedby/<string:address>')
class AssetLikedByItem(Resource):
    """ Get assets for likedby methods """
    def get(self, address):
        """ Get liked assets for user """
        return AssetLikes().get_liked_assets(address)

@NS.route('/filtered')
class AssetFilterCollection(Resource):
    """ Assets Filter Collection methods """
    @NS.doc(parser=FILTER_PARSER, body=ASSET_FILTER_MODEL)
    @NS.expect(ASSET_FILTER_MODEL, validate=True)
    def post(self):
        """ Return list of filtered assets """
        args = FILTER_PARSER.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        print(limit)
        return Asset().get_all_sorted_filtered(request.json, limit=limit, offset=offset)


@NS.route('/buy')
class BuyCollection(Resource):
    """ Buy Collection methods """
    @NS.expect(BUY_MODEL, validate=True)
    def post(self):
        """ Perform buy transaction """
        return Transaction().process_buy_transaction(request.json)


@NS.route('/transfer')
class TransferCollection(Resource):
    """ Transfer Collection methods """
    @NS.expect(TRANSFER_MODEL, validate=True)
    def post(self):
        """ Perform tranfer transaction """
        return Transaction().process_transfer_transaction(request.json)


@NS.route('/mint')
class MintCollection(Resource):
    """ Mint Collection methods """
    @NS.expect(MINT_MODEL, validate=True)
    def post(self):
        """ Minted  assets """
        return Transaction().process_mint_transaction(request.json)


@NS.route('/burn')
class BurnCollection(Resource):
    """ Burn Collection methods """
    @NS.expect(BURN_MODEL, validate=True)
    def post(self):
        """ Burn  asset """
        return Transaction().process_burn_transaction(request.json)


@NS.route('/list')
class ListCollection(Resource):
    """ List Collection methods """
    @NS.expect(LIST_MODEL, validate=True)
    def post(self):
        """ List  assets """
        return Transaction().list_asset(request.json) 


# @NS.route('/web3/<string:hash>')
# class Web3Collection(Resource):
#     """ Web3 Collection methods """
#     def get(self, hash):
#         """ Web3 get receipt """
#         return Web3Alley().get_transaction_receipt(hash)


# @NS.route("/verifiedartistesasset")
# class VerifyArtistesAssets(Resource):
#     """List of asset which are minted by verifyed artistes """ 
#     def get(self):
#         """ List of Assets """
#         return Asset().get_all_verify_assets_artistes()       
@NS.route('/latestImages')
class LatestImagesCollection(Resource):
    @NS.doc(parser=FILTER_PARSER)
    def get(self):
        """ Return only latest images of assets """
        args = FILTER_PARSER.parse_args()
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        return Asset().latest_image_assets(limit=limit,offset=offset)
@NS.route('/collectionAssets')
class NftBelongsToCollection(Resource):
    @NS.doc(parser=PARSER_COLLECTION)
    def get(self):
        """ Return assets which belongs to a collection"""
        args= PARSER_COLLECTION.parse_args()
        collectionId=args.get('collectionId')
        limit= args.get('limit',None)
        offset = args.get('offset', None)
        return Asset().get_nft_list_from_collection(collectionId=collectionId,limit=limit,offset=offset)        
