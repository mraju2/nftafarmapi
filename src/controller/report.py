""" Assets Endpoint """
from flask import request
from flask_restx import Namespace, Resource, fields, inputs, reqparse

from service.report import Report
from util.jwt_auth import check_apis_are_protected_or_open
from util.utils import load_json_schema

JWT_REQUIRED, JWT_REFRESH_TOKEN_REQUIRED = check_apis_are_protected_or_open()

NS = Namespace(
    'report',
    description='Operations related to assets')


# REPORT_MODEL=NS.model('Report',{
#     'assetId':fields.String(
#         required=True,
#         descrption="Asset Id"
#     ),
#     'message':fields.String(
#         required=True,
#         descrption="Message for report "
#     ),
#     'sign':fields.String(
#         required=True,
#         descrption="Signature of user"
#     ),
#     'reporter':fields.String(
#         required=True,
#         descrption="reporter"
#     ),
#     'reportReasonList':fields.List(
#         fields.String,
#         required=False,
#         description="list of reason for reporting NFT"
#     )
# })
REPORT_MODEL=NS.schema_model('Report',load_json_schema('report_schema.json'))


PARSER = reqparse.RequestParser()
PARSER.add_argument(
    'assetId', type=str, required=False,
    help='Get reports with assetId'
)


@NS.route('/')
class ReportCollection(Resource):
    """ Report Collection methods """
    # @NS.doc(parser=PARSER)
    # def get(self):
    #     """ Return list of reports """
    #     args = PARSER.parse_args()
    #     assetId= args.get('assetId', None)
    #     return Report().get_all(assetId=assetId)

    @NS.expect(REPORT_MODEL, validate=True)
    def post(self):
        """ Report asset """
        return Report().create_report(request.json)


@NS.route('/<string:reportId>')
class ReportItem(Resource):
    """ Report Item methods """
    def get(self, reportId):
        """ Get a report """
        return Report().get_one(reportId)

@NS.route('/assetId/<string:assetId>')
class ReportAsset(Resource):
    """ Report Item methods """
    def get(self, assetId):
        """ Get a report """
        return Report().get_all(assetId)        