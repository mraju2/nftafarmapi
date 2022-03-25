""" Asset Likes and Views Service """
from pymongo.errors import DuplicateKeyError
from settings import USE_MONGO
from service.service_base import ServiceBase
from service.asset import Asset
import traceback


class AssetLikes(ServiceBase):
    """ Asset Likes and Views Service """        

    def update_like(self, data):
        """ Update like in asset """
        try:
            item, status = self.get_one(data['assetId'])
            request_payload = item if status == 200 else {"assetId": data['assetId'], "likes": [], "likesCount" : 0}
            if data['like'] is True:
                request_payload['likes'].append(data['address'])
                request_payload['likesCount'] += 1
            elif data['like'] is False:
                request_payload['likes'].remove(data['address'])
                request_payload['likesCount'] -= 1

            if status == 200:
                self.update_one(data['assetId'], request_payload)
            else:
                self.create_one(request_payload)
            
            Asset().update_one(data['assetId'], {'likesCount': request_payload['likesCount']})
            self.logger.info(f"Asset {data['assetId']} got one more likes")
            return {"message": f"Likes updated successfully for {data['assetId']}"}, 200
        except Exception:
            return {
                "error": f"Something went wrong, Exception : {traceback.format_exc()}"
            }, 503

    def update_views(self, data):
        """ Update like in asset """
        try:
            item, status = Asset().get_one(data['assetId'])
            if status != 200:
                return {"error": f"Asset {data['assetId']} not found"}, 404

            if 'views' in item:
                item['views'] += 1
            else:
                item['views'] = 1
            
            Asset().update_one(data['assetId'], {'views': item['views']})
            self.logger.info(f"Asset {data['assetId']} got viewed")
            return {"message": f"Views updated successfully for {data['assetId']}"}, 200
        except Exception:
            return {
                "error": f"Something went wrong, Exception : {traceback.format_exc()}"
            }, 503

    def get_one(self, assetId):
        """ Return a assetLike entry """
        item = self.collection.find_one({'assetId': assetId}, {'_id': 0})

        if item:
            return item, 200

        return {
            'error': f"Asset {assetId} not found"
        }, 400

    def get_liked_assets(self, address):
        """ Return liked assets for user """
        items = list(self.collection.find({'likes': address}, {'assetId': 1, '_id': 0}))
        assetIds = [item['assetId'] for item in items]

        return {"items": assetIds}, 200
    
    def create_one(self, data):
        """ Create a asset """
        get_one = self.get_one(data['assetId'])
        if get_one[1] == 200:
            return {
                'error': f"Asset {data['assetId']} already exists"
            }, 409

        # Create document
        try:
            self.collection.insert_one(data)
        except DuplicateKeyError:
            return {
                'error': f"Asset {data['assetId']} already exists"
            }, 409

        if '_id' in data:
            del data['_id']
        # created successfully
        return {
            'message': f"Asset {data['assetId']} created successfully",
            'data': data
        }, 201
        

    def update_one(self, assetId, data):
        """ Update a Asset """

        # pylint: disable=len-as-condition
        result = self.collection.update_one(
            {'assetId': assetId},
            {'$set': data})
        if result.matched_count:
            if result.modified_count:
                return {
                    'message': f'Asset {assetId} changed',
                    'data': data
                }, 200
            return {
                'message': f'Asset {assetId} updated',
                'data': data
            }, 200
        return {
            'error': f'Asset {assetId} not found'
        }, 404

    def delete_one(self, assetId):
        """ Delete a Asset Like entry """
        result = self.collection.delete_one({'assetId': assetId})
        if result.deleted_count:
            return {
                'message': f'Asset {assetId} deleted'
            }, 200

        return {
            'error': f'Asset {assetId} not found'
        }, 404
