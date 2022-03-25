from flask import request
from flask_restx import Namespace, Resource, fields, inputs, reqparse
from service.report import Report
from util.jwt_auth import check_apis_are_protected_or_open
from util.utils import load_json_schema
from service.report_nft_delist import ReportNftDelist
NS = Namespace(
    'reportNftDelist',
    description='Operations related to Delist or List NFT which are reported')

REPORT_NFT_DELIST_MODEL=NS.model('ReportNFTDelist',{
    'assetId':fields.String(
        required=True,
        descrption="Asset Id"
    ),
    'listed':fields.Boolean(
        required=True,
        descrption="Listed for True and DeList for False"
    ),
    'reportId':fields.String(
        required=True,
        description="report Id "
    )
})
@NS.route('/')
class ReportNftDelistCollection(Resource):
    """ Report Collection methods """
    @NS.expect(REPORT_NFT_DELIST_MODEL, validate=True)
    def post(self):
        """ Report asset """
        return ReportNftDelist().get_update_asset(request.json)

