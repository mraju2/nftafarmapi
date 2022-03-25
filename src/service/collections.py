""" Collections Service"""
from pymongo.errors import DuplicateKeyError
from settings import USE_MONGO,BLOCK_CHAIN
from service.service_base import ServiceBase
from service.profile import Profile
from service.asset import Asset
import traceback
from datetime import datetime, timezone
from service.web3 import Web3Alley
import uuid
from settings import BLOCK_CHAIN

class Collection(ServiceBase):
    """Collection Service"""
    def get_all(self, creatorId=None, limit=None, offset=None):
        """ Get all assets """
        try:
            query = {}
            output = {}
            if creatorId:
                query['creatorId'] = {'$regex': creatorId, '$options': 'i'}
            if offset and limit:
                output['offset'] = offset
                output['limit'] = limit
                output['items'] = list(self.collection
                                    .find(query, {'_id': 0})
                                    .sort('_id', -1)
                                    .skip(int(offset))
                                    .limit(int(limit)))
            else:
                output['items'] = list(self.collection.find(query, {'_id': 0}).sort('_id', -1))
            for asset in output['items']:
                try:
                    nft_count, nft_count_status = Asset().get_nft_count_from_collection(asset['id'].lower())
                    asset.update({'total_nft_count': nft_count})
                except Exception:
                    self.logger.error(f"Something went wrong")    

            return output, 200
        except Exception:
            self.logger.error(f"Something went wrong, Exception : {traceback.format_exc()}")
            return {
                "error": f"Something went wrong, Exception"
            }, 503    


    def get_one_by_collectionName(self,collectionName):
        """ Return a collections """
        try:
            item = self.collection.find_one({'collectionName': collectionName}, {'_id': 0})
            if item:
                self.logger.info(f"Collection {collectionName} found")
                return item, 200
            self.logger.error(f"collection {collectionName} not found")
            return {
            'error': f"Collection {collectionName} not found"
            }, 400
            
        except Exception:
            self.logger.error(f"Something went wrong while fetching CollectionName,Exception : {traceback.format_exc()}")
            return {
                "error": f"Something went wrong, Exception"
            }, 503 

    def get_one_by_collectionId(self, id):
        """ Get a collection"""
        try:
            item = self.collection.find_one({'id':id}, {'_id': 0})
            if item:
                self.logger.info(f"Collection {id} found")
                nft_count, nft_count_status = Asset().get_nft_count_from_collection(item['id'].lower())
                item.update({"total_nft_count":nft_count})
                return item, 200
            self.logger.error(f"Collection {id} not found")
            return {
            'error': f"Collection {id} not found"
            }, 400
            
        except Exception:
            self.logger.error(f"Something went wrong while fetching CollectionName,Exception : {traceback.format_exc()}")
            return {
                "error": f"Something went wrong, Exception"
            }, 503  
    
    def create_one(self, data):
        """ Create a asset """
        get_one = self.get_one_by_collectionName(data['collectionName'])
        if get_one[1] == 200:
            self.logger.error(f"Collection {data['collectionName']} already exists")
            return {
                'error': f"Collection {data['collectionName']} already exists"
            }, 409
        # Create document
        
        collection_payload={
                            "id":str(uuid.uuid4()),
                            "onSale":data['onSale'],
                            "creatorId":data['creatorId'].lower(),
                            "collectionName":data['collectionName'],
                            "description":data['description'],
                            "startDate":data["startDate"],
                            "createdAtTime":str(datetime.now(timezone.utc).timestamp()),
                            "collectionLogo":data["collectionLogo"],
                            "collectionBanner":data["collectionBanner"]
                            }
        data['id']=collection_payload['id']                    
        try:
            if data['onSale'] and data['basePrice'] and data['priceUnit']:
                collection_payload['basePrice']=data['basePrice']
                collection_payload['priceUnit']=data['priceUnit']
        except KeyError:
            self.logger.error(f"basePrice,priceUnit are required property")
            return {
                    "errors": {
                    "basePrice": "basePrice is a required property",
                    "priceUnit": "priceUnit is a required property"
                  },
                    "message": "Input payload validation failed"
                },400       
        try:
            self.collection.insert_one(collection_payload)
            self.logger.info(f"Collection {collection_payload['id']} created successfully")
        except DuplicateKeyError:
            self.logger.error(f"Collection {collection_payload['id']} already exists: {traceback.format_exc()}")
            return {
                'error': f"Collection {collection_payload['id']} already exists"
            }, 409
        except Exception as ex:
            self.logger.error(f"Something went wrong while creating collection,Exception : {traceback.format_exc()}")
            return {
                'error': f"Error occured while creating collection {data['collectionName']} "
            }, 503
        if '_id' in data:
            del data['_id']
        # created successfully
        return {
            'message': f"Collection {collection_payload['id']} created successfully",
            'data': data
        }, 201


    def delete_one(self,Id):
        """ Delete a Collection """
        try:
            collection_details,collection_status=self.get_one_by_collectionId(Id)
            if collection_status !=200:
                self.logger.error(f'Collection {Id} not found')
                return {
                    'error': f'Collection {Id} not found'
                }, 404

            if collection_status == 200 and collection_details['total_nft_count'] == 0:
                result = self.collection.delete_one({'id':Id})
                if result.deleted_count:
                    self.logger.info(f'Collection {Id} deleted')
                    return {
                        'message': f'Collection {Id} deleted'
                    }, 200
                self.logger.error(f'Collection {Id} not found')
                return {
                    'error': f'Collection {Id} not found'
                }, 404
            self.logger.error(f"Collection {Id} have more then 1 NFT, so we can't deleted the collection")    
            return {
                'message':f"Collection {Id} have more then 1 NFT, so you can't deleted the collection"
            },400 
        except Exception:
            self.logger.error(f"Something went wrong while updating collection,Exception : {traceback.format_exc()}")
            return {
                'error': f"Error occured while deleting collection {Id} "
            }, 503       
        

    def update_one(self,Id, data):
        """ Update a collection """
        try:
            collection,collection_status=self.get_one_by_collectionId(Id)
            if collection_status != 200:
                self.logger.error(f"Collection {Id} is not found")
                return collection,collection_status
            payload = {}
            if 'collectionName' in data:
                payload['collectionName'] = data['collectionName']      
            if 'description' in data:
                payload['description'] = data['description']
            if 'startDate' in data:
                payload['startDate'] = data['startDate']
            if 'collectionLogo' in data:
                payload['collectionLogo'] = data['collectionLogo']
            if 'collectionBanner' in data:
                payload['collectionBanner']=data['collectionBanner']
            try:
                if data['onSale']:
                    payload['onSale']=data['onSale']
                    payload['basePrice']=data['basePrice']
                    payload['priceUnit']=data['priceUnit']
                else:
                    payload['onSale']=data['onSale']
            except KeyError:
                self.logger.error(f"basePrice and priceUnit required, error: KeyError")
                return {
                        "errors": {
                        "basePrice": "basePrice is a required property",
                        "priceUnit": "priceUnit is a required property"
                    },
                        "message": "Input payload validation failed"
                    },400          


            # pylint: disable=len-as-condition
            result = self.collection.update_one(
                {'id':Id},
                {'$set': payload})
            if result.matched_count:
                if result.modified_count:
                    return {
                        'message': f'Collection {Id} changed',
                        'data': data
                    }, 200
                return {
                    'message': f'collection {Id} updated',
                    'data': data
                }, 200
                self.logger.info(f"Collection {Id} updated")
            self.logger.error(f"Collection {Id} not found")   
            return {
                'error': f'Collection {Id} not found'
            }, 404
        except Exception:
            self.logger.error(f"Something went wrong while updating collection,Exception : {traceback.format_exc()}")
            return {
                'error': f"Error occured while updating collection {data['collectionName']} "
            }, 503

    