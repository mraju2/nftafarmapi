""" Asset Service """
from pymongo.errors import DuplicateKeyError
from settings import USE_MONGO
from service.service_base import ServiceBase
import traceback

class AssetArchived(ServiceBase):
    """ Asset Service """

    def get_all(self):
        """ Get all assets """
        items = list(self.collection.find({}, {'_id': 0}).sort('_id', -1))

        return {"items": items}, 200

    
    def get_count(self):
        """ Get count of """
        output = self.collection.find({}, {'_id': 0}).count()
            
        return {"count": output}, 200


    def get_one(self, assetId):
        """ Return a assets """
        item = self.collection.find_one({'id': assetId}, {'_id': 0})

        if item:
            self.logger.info(f"Asset {assetId} found")
            return item, 200

        self.logger.info(f"Asset {assetId} not found")
        return {
            'error': f"Asset {assetId} not found"
        }, 400


    def create_one(self, data):
        """ Create a asset """
        get_one = self.get_one(data['id'])
        if get_one[1] == 200:
            return {
                'error': f"Asset {data['id']} already exists"
            }, 409

        # Create document
        try:
            self.collection.insert_one(data)
        except DuplicateKeyError:
            return {
                'error': f"Asset {data['id']} already exists"
            }, 409

        if '_id' in data:
            del data['_id']
        # created successfully
        return {
            'message': f"Asset {data['id']} created successfully",
            'data': data
        }, 201


    def delete_one(self, assetId):
        """ Delete a Asset """
        result = self.collection.delete_one({'id': assetId})
        if result.deleted_count:
            return {
                'message': f'Asset {assetId} deleted'
            }, 200

        return {
            'error': f'Asset {assetId} not found'
        }, 404
        

    def update_one(self, assetId, data):
        """ Update a Asset """

        # pylint: disable=len-as-condition
        result = self.collection.update_one(
            {'id': assetId},
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
