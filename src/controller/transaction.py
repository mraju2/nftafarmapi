""" Transactions Endpoint """
from flask import request
from flask_restx import Namespace, Resource, fields, inputs, reqparse

from service.transaction import Transaction
from util.jwt_auth import check_apis_are_protected_or_open
from util.utils import load_json_schema

JWT_REQUIRED, JWT_REFRESH_TOKEN_REQUIRED = check_apis_are_protected_or_open()

NS = Namespace(
    'transactions',
    description='Operations related to transactions')

TRANSACTION_MODEL = NS.schema_model('Transaction', load_json_schema('transaction-schema.json'))

PROCESS_MODEL = NS.schema_model('Process', load_json_schema('process-schema.json'))

PARSER = reqparse.RequestParser()
PARSER.add_argument(
    'assetId', type=str, required=False,
    help='Get transactions with assetId'
)
PARSER.add_argument(
    'user', type=str, required=False,
    help='Get transactions with user'
)

@NS.route('/')
class TransactionCollection(Resource):
    """ Transactions Collection methods """
    @NS.doc(parser=PARSER)
    def get(self):
        """ Return list of transactions """
        args = PARSER.parse_args()
        assetId= args.get('assetId', None)
        user= args.get('user', None)
        return Transaction().get_all(assetId=assetId, user=user)

    # @NS.expect(TRANSACTION_MODEL, validate=True)
    # @JWT_REQUIRED
    # def post(self):
    #     """ Creates a transaction """
    #     return Transaction().create_one(request.json)


@NS.route('/failed')
class FailedTransactionCollection(Resource):
    """ Failed Transactions Collection methods """
    @NS.doc(parser=PARSER)
    def get(self):
        """ Return list of failed transactions """
        args = PARSER.parse_args()
        assetId= args.get('assetId', None)
        user= args.get('user', None)
        return Transaction().get_all_failed(assetId=assetId, user=user)


@NS.route('/<string:transactionId>')
class TransactionItem(Resource):
    """ Transaction Item methods """
    def get(self, transactionId):
        """ Get a transaction """
        return Transaction().get_one(transactionId)

    # @JWT_REQUIRED
    # def delete(self, transactionId):
    #     """ Delete a transaction """
    #     return Transaction().delete_one(transactionId)

    # @NS.expect(TRANSACTION_MODEL, validate=True)
    # @JWT_REQUIRED
    # def put(self, transactionId):
    #     """ Update a transaction """
    #     return Transaction().update_one(transactionId, request.json)

# @NS.route('/process')
# class ProcessCollection(Resource):
#     """ Processes Collection methods """
#     @NS.expect(PROCESS_MODEL, validate=True)
#     @JWT_REQUIRED
#     def post(self):
#         """ Processes a transaction """
#         if request.json['lastTransactionStatus'].lower() == 'failed':
#             return Transaction().process_failed_transaction(request.json)
#         else:
#             return Transaction().process_transaction(request.json)