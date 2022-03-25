""" Offers Endpoint """
from flask import request
from flask_restx import Namespace, Resource, fields, inputs, reqparse

from service.offer import Offer
from util.jwt_auth import check_apis_are_protected_or_open
from util.utils import load_json_schema
from service.transaction import Transaction

JWT_REQUIRED, JWT_REFRESH_TOKEN_REQUIRED = check_apis_are_protected_or_open()

NS = Namespace(
    'bid',
    description='Operations related to offers')

ASSET_MODEL = NS.schema_model('Offer', load_json_schema('bid-schema.json'))
BID_ACCEPT_MODEL = NS.model('BidAccept',
            {
                'bidId': fields.String(
                    required=True,
                    descrption="Bid id"
                ),
                'hash': fields.String(
                    required=True,
                    descrption="Bid Transaction Hash"
                )
            }
        )
BID_CANCEL_MODEL = NS.model('BidCancel',
            {
                'bidId': fields.String(
                    required=True,
                    descrption="Bid id"
                ),
                'sign': fields.String(
                    required=True,
                    descrption="Signature for cancelling bid"
                )
            }
        )
BID_PLACE_MODEL=NS.schema_model("BidPlace",load_json_schema('bid-place-schema.json'))        

PARSER = reqparse.RequestParser()
PARSER.add_argument(
    'assetId', type=str, required=False,
    help='Get offers with assetId'
)
PARSER.add_argument(
    'user', type=str, required=False,
    help='Get offers with user'
)

@NS.route('/')
class OfferCollection(Resource):
    """ Offers Collection methods """
    @NS.doc(parser=PARSER)
    def get(self):
        """ Return list of offers """
        args = PARSER.parse_args()
        assetId= args.get('assetId', None)
        user= args.get('user', None)
        return Offer().get_all(assetId=assetId, user=user)

    # @NS.expect(ASSET_MODEL, validate=True)
    # @JWT_REQUIRED
    # def post(self):
    #     """ Creates a offer """
    #     return Offer().create_one(request.json)


@NS.route('/<string:offerId>')
class OfferItem(Resource):
    """ Offer Item methods """
    def get(self, offerId):
        """ Get a offer """
        return Offer().get_one(offerId)

    # @JWT_REQUIRED
    # def delete(self, offerId):
    #     """ Delete a offer """
    #     return Offer().delete_one(offerId)

    # @NS.expect(ASSET_MODEL, validate=True)
    # @JWT_REQUIRED
    # def put(self, offerId):
    #     """ Update a offer """
    #     return Offer().update_one(offerId, request.json)

@NS.route('/accept')
class BidAcceptCollection(Resource):
    """ Bid Collection accept methods """

    @NS.expect(BID_ACCEPT_MODEL, validate=True)
    @JWT_REQUIRED
    def post(self):
        """ Accept a bid """
        return Transaction().process_bid_transaction(request.json)

@NS.route('/cancel')
class BidCancelCollection(Resource):
    """ Bid Collection cancel methods """

    @NS.expect(BID_CANCEL_MODEL, validate=True)
    @JWT_REQUIRED
    def post(self):
        """ Cancel a bid """
        return Offer().cancel_bid(request.json)
        
@NS.route('/place')
class BidPlaceCollection(Resource):
    """ Bid Collection place methods """

    @NS.expect(BID_PLACE_MODEL, validate=True)
    @JWT_REQUIRED
    def post(self):
        """ Place a bid """
        return Offer().place_bid(request.json)                