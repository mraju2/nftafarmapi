""" Report Service """
from pymongo.errors import DuplicateKeyError, ExecutionTimeout
from settings import USE_MONGO
from service.service_base import ServiceBase
import traceback
from datetime import datetime, timezone
import uuid
from service.asset import Asset
from service.web3 import Web3Alley


class Report(ServiceBase):
    """ Report Service """

    def get_all(self, assetId=None):
        """ Get all assets """
        query = {}
        output = {}
        if assetId:
            query['assetId'] = {'$regex': assetId, '$options': 'i'}

        output['items'] = list(self.collection.find(query, {'_id': 0}).sort('_id', -1))
            
        return output, 200


    def get_one(self, reportId):
        """ Return a report """
        item = self.collection.find_one({'id': reportId}, {'_id': 0})

        if item:
            return item, 200

        return {
            'error': f"Report {reportId} not found"
        }, 400

    def get_one_assetId(self,assetId):
        
        item=self.collection.find_one({'assetId':assetId},{'_id':0})

        if item:
            return item,200
        return {
            'error':f"Asset {assetId} not found in report list"
        },400    

    def create_one(self, data):
        """ Create a Report """
        get_one = self.get_one(data['id'])
        if get_one[1] == 200:
            return {
                'error': f"Report {data['id']} already exists"
            }, 409

        # Create document
        try:
            self.collection.insert_one(data)
        except DuplicateKeyError:
            return {
                'error': f"Report {data['id']} already exists"
            }, 409

        if '_id' in data:
            del data['_id']
        # created successfully
        return {
            'message': f"Report {data['id']} created successfully",
            'data': data
        }, 201


    def create_report(self, data):
        """ Create Report """
        try:
            asset, asset_status_code = Asset().get_one(data['assetId'])
            if asset_status_code != 200:
                return asset, asset_status_code
            msg = f"You are about to Report nft: {data['assetId']}"
            signed_owner = Web3Alley().read_sign(msg, data['sign'])
            if signed_owner.lower() != data['reporter'].lower():
                return {"error": "Not a trusted request"}, 400
            payload={}
            if 'reportReasonList' in data:
                payload = {
                'id': str(uuid.uuid4()),
                'assetId': data['assetId'],
                'message': data['message'],
                'sign': data['sign'],
                'reporter': data['reporter'],
                'reportReasonList': data['reportReasonList'],
                'date': str(datetime.now(timezone.utc).timestamp())
                }
            else:
                payload = {
                    'id': str(uuid.uuid4()),
                    'assetId': data['assetId'],
                    'message': data['message'],
                    'sign': data['sign'],
                    'reporter': data['reporter'],
                    'date': str(datetime.now(timezone.utc).timestamp())
                }
            response = self.create_one(payload)
            return response
        except Exception:
            self.logger.error(f"Failure in create_report method for {data['assetId']}, Exception : {traceback.format_exc()}")
            return {
                "error": f"Something went wrong with the report creation for {data['assetId']}"
            }, 503


    def delete_one(self, reportId):
        """ Delete a Report """
        result = self.collection.delete_one({'id': reportId})
        if result.deleted_count:
            return {
                'message': f'Report {reportId} deleted'
            }, 200

        return {
            'error': f'Report {reportId} not found'
        }, 404
        

    def update_one(self, reporterId, data):
        """ Update a Report """

        # pylint: disable=len-as-condition
        result = self.collection.update_one(
            {'id': reporterId},
            {'$set': data})
        if result.matched_count:
            if result.modified_count:
                return {
                    'message': f'Report {reporterId} changed',
                    'data': data
                }, 200
            return {
                'message': f'Report {reporterId} updated',
                'data': data
            }, 200
        return {
            'error': f'Report {reporterId} not found'
        }, 404
