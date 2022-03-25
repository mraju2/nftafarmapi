""" Asset Service """
from pymongo.errors import DuplicateKeyError
from settings import USE_MONGO,BLOCK_CHAIN
from service.service_base import ServiceBase
from service.profile import Profile
import traceback
from datetime import datetime, timezone
from service.web3 import Web3Alley
import uuid
from settings import BLOCK_CHAIN


class Asset(ServiceBase):
    """ Asset Service """

    def search(self, search_text, limit=None):
        """ Search assets, profiles """
        try:
            output = {}
            output['assets'] = self.search_assets(search_text, limit)[0]['items']
            output['profiles'] = Profile().search_profiles(search_text, limit)[0]['items']
            return output, 200
        except Exception:
            return {
                "error": f"Something went wrong, Exception : {traceback.format_exc()}"
            }, 503

    def search_assets(self, search_text, limit=None):
        """ Search assets """
        query = {
            'status': 'success',
            'listed': {'$ne': False},
            '$or': [
                    {'id': {'$regex': '.*'+ search_text + '.*', '$options': 'i'}},
                    {'item.name': {'$regex': '.*'+ search_text + '.*', '$options': 'i'}},
                    {'item.description': {'$regex': '.*'+ search_text + '.*', '$options': 'i'}}
                ]
            }
        output = {}
        if limit:
            output['items'] = list(self.collection
                                    .find(query, {'_id': 0})
                                    .sort('_id', -1)
                                    .limit(int(limit)))
        else:
            output['items'] = list(self.collection
                                    .find(query, {'_id': 0})
                                    .sort('_id', -1))

        return output, 200



    # def get_all_today_minted(self):
    #     """ Get all with likes """
    #     today = str(datetime.now(timezone.utc).replace(hour=0,minute=0,second=0,microsecond=0).timestamp())
    #     type = "bid"
    #     output = list(self.collection
    #                     .aggregate([
    #                         {'$lookup':
    #                             {
    #                             'from': "transaction",
    #                             'let': {"asset_id": "$id", "status": "$status"},
    #                             'pipeline': [
    #                                 {'$match': 
    #                                     {"$expr":
    #                                         {"$and":
    #                                             [
    #                                                 { "$eq": [ "$assetId",  "$$asset_id" ] },
    #                                                 { "$eq": [ "$$status",  "success" ] },
    #                                                 { "$eq": ["$type", type]},
    #                                                 { "$gte": ["$date", today]}
    #                                             ]            
    #                                         }
    #                                     }
    #                                 },
    #                                 { '$project': { '_id': 0 } }
    #                             ],
    #                             'as': "fromItems"
    #                             }
    #                         },
    #                         {
    #                             '$replaceRoot': 
    #                                 { 'newRoot': 
    #                                     { '$mergeObjects': 
    #                                         [ 
    #                                             { '$arrayElemAt': [ "$fromItems", 0 ] }, 
    #                                             "$$ROOT" 
    #                                         ] 
    #                                     }
    #                                 }
    #                         },
    #                         {
    #                             '$unwind': {
    #                                 "path": "$fromItems",
    #                                 "preserveNullAndEmptyArrays": False
    #                             }
    #                         },
    #                         { '$project': { "fromItems": 0,'_id': 0 } }
    #                     ])   
    #                 )
        
    #     return {"output": output}, 200

    # def get_all_verify_assets_artistes(self, limit=None, offset=None):
    #     """ Get all with likes """
    #     #today = str(datetime.now(timezone.utc).replace(hour=0,minute=0,second=0,microsecond=0).timestamp())
    #     #type = "bid"
    #     output = list(self.collection
    #                     .aggregate([
    #                         {'$lookup':
    #                             {
    #                             'from': "profile",
    #                             'let': {"creator": "$creator","owners":"$owners", "status": "$status"},
    #                             'pipeline': [
    #                                 {'$match': 
    #                                     {"$expr":
    #                                         {"$and":
    #                                             [
    #                                                 {"$or":[
    #                                                     { "$eq": [ "$address",  "$$creator" ] },
    #                                                     { "$eq": [ "$address",  "$$owners" ]}
    #                                                        ]
    #                                                 },
    #                                                 {"$eq": ["$$status", "success"]},
    #                                                 { "$eq": ["$verified", True ]}
                                                    
    #                                             ]            
    #                                         }
    #                                     }
    #                                 },
    #                                 { '$project': { '_id': 0,'address':1, "verified":1, } }
    #                             ],
    #                             'as': "fromItems"
    #                             }
    #                         },
    #                         {
    #                             '$replaceRoot': 
    #                                 { 'newRoot': 
    #                                     { '$mergeObjects': 
    #                                         [ 
    #                                             { '$arrayElemAt': [ "$fromItems", 0 ] }, 
    #                                             "$$ROOT" 
    #                                         ] 
    #                                     }
    #                                 }
    #                         },
    #                         {
    #                             '$unwind': {
    #                                 "path": "$fromItems",
    #                                 "preserveNullAndEmptyArrays": False
    #                             }
    #                         },
    #                         {"$sort": {'_id': -1}},
    #                         {"$skip": int(offset)},
    #                         {"$limit": int(limit)},
    #                         { '$project': { "fromItems": 0,'_id': 0 } },
    #                     ])   
    #                 )
        
    #     return {"items": output}, 200    


    def get_todays_assets(self, limit=None, offset=None):
        """ Get todays assets """
        today = str(datetime.now(timezone.utc).replace(hour=0,minute=0,second=0,microsecond=0).timestamp())
        output = {}
        output['offset'] = offset
        output['limit'] = limit
        output['items'] = list(self.collection
                        .find({"status": "success", "mintTime": {"$gte" : today}}, {'_id': 0})
                        .sort({'_id', -1})
                        .skip(int(offset))
                        .limit(int(limit)))
        return output, 200
    
    def get_on_sale_assets(self, onSale=True, limit=None, offset=None):
        """ Get on sale assets """
        output = {}
        output['offset'] = offset
        output['limit'] = limit
        output['items'] = list(self.collection
                        .find({"status": "success", "onSale": onSale}, {'_id': 0})
                        .sort({'_id', -1})
                        .skip(int(offset))
                        .limit(int(limit)))
        return output, 200
    
    def get_on_sale_with_currency(self, priceUnit=BLOCK_CHAIN ,limit=None, offset=None):
        """ Get on sale assets """
        output = {}
        output['offset'] = offset
        output['limit'] = limit
        output['items'] = list(self.collection
                        .find({"status": "success", "onSale": True, "priceUnit": priceUnit}, {'_id': 0})
                        .sort({'_id', -1})
                        .skip(int(offset))
                        .limit(int(limit)))
        return output, 200

    def get_most_liked(self, limit=None, offset=None):
        """ Get most liked assets """
        output = {}
        output['offset'] = offset
        output['limit'] = limit
        output['items'] = list(self.collection
                        .find({"status": "success"}, {'_id': 0})
                        .sort('likesCount', -1)
                        .skip(int(offset))
                        .limit(int(limit)))
        return output, 200

    def get_most_viewed(self, limit=None, offset=None):
        """ Get most viewed assets """
        output = {}
        output['offset'] = offset
        output['limit'] = limit
        output['items'] = list(self.collection
                        .find({"status": "success"}, {'_id': 0})
                        .sort('views', -1)
                        .skip(int(offset))
                        .limit(int(limit)))
        return output, 200

    def get_sorted_by_price(self, sortBy="high", priceUnit=BLOCK_CHAIN, limit=None, offset=None):
        """ Get sorted by price """
        sortValue = -1 if sortBy == "high" else 1
        output = {}
        output['offset'] = offset
        output['limit'] = limit
        output['items'] = list(self.collection
                        .find({"status": "success", "onSale": True, "priceUnit": priceUnit}, {'_id': 0})
                        .sort({'price', sortValue})
                        .skip(int(offset))
                        .limit(int(limit)))
        return output, 200

    def get_sorted_by_bid_price(self, sortBy="high", priceUnit="wBNB", limit=None, offset=None):
        """ Get sorted by price """
        sortValue = -1 if sortBy == "high" else 1
        output = {}
        output['offset'] = offset
        output['limit'] = limit
        output['items'] = list(self.collection
                        .find({"status": "success", "bidStatus": "active"}, {'_id': 0})
                        .sort({f"highestBid{priceUnit}", sortValue})
                        .skip(int(offset))
                        .limit(int(limit)))
        return output, 200

    def get_all_sorted_filtered(self, data, limit="20", offset="0"):
        """ Get all sorted or filtered """
        try:
            
            find_query = {}
            sort_query = []
            if data['filterBy'] == "todaysAssets":
                today = str(datetime.now(timezone.utc).replace(hour=0,minute=0,second=0,microsecond=0).timestamp())
                find_query = {"status": "success", 'listed': {'$ne': False}, "mintTime": {"$gte" : today}}
                sort_query = [('_id', -1)]
            elif data['filterBy'] == "recentlyAdded":
                find_query = {"status": "success", 'listed': {'$ne': False}}
                sort_query = [('_id', -1)]
            elif data['filterBy'] == "onSale":
                find_query = {"status": "success", 'listed': {'$ne': False}, "onSale": data['onSale']}
                sort_query = [('_id', -1)]
            elif data['filterBy'] == "currency":
                find_query = {"status": "success", 'listed': {'$ne': False}, "onSale": True, "priceUnit": data['priceUnit']}
                sort_query = [('_id', -1)]
            elif data['filterBy'] == "mostLiked":
                find_query = {"status": "success", 'listed': {'$ne': False}, "likesCount": {"$exists": True}}
                sort_query = [('likesCount', -1)]
            elif data['filterBy'] == "mostViewed":
                find_query = {"status": "success", 'listed': {'$ne': False}, "views": {"$exists": True}}
                sort_query = [('views', -1)]
            elif data['filterBy'] == "salePrice":
                sortValue = 1 if data['sortAssending'] == True else -1
                find_query = {"status": "success", 'listed': {'$ne': False}, "onSale": True, "priceUnit": data['priceUnit']}
                sort_query = [('price', sortValue)]
            elif data['filterBy'] == "bidPrice":
                sortValue = 1 if data['sortAssending'] == True else -1
                find_query = {"status": "success", 'listed': {'$ne': False}, "bidStatus": "active", f"highestBid{data['priceUnit']}": {"$exists": True}}
                sort_query = [(f"highestBid{data['priceUnit']}", sortValue)]
            elif data['filterBy'] == 'verifiedArtist':
                verified_artists = Profile().get_all_verified_addresses()
                find_query = {
                    'status': 'success',
                    'listed': {'$ne': False},
                    '$or': [
                            {'creator': {'$in': verified_artists}},
                            {'owners': {'$in': verified_artists}}
                        ]
                    }
                sort_query = [('_id', -1)]

            # if data['filterBy'] == 'verifiedArtist':
            #     verified_assets,c_status=self.get_all_verify_assets_artistes(limit=int(limit),offset=int(offset))
            #     output_items = []
            #     for asset in verified_assets['items']:
            #         try:
            #             if not ('listed' in asset and asset['listed'] == False):
            #                 creator, c_status = Profile().get_one_verified_info(asset['creator'].lower())
            #                 owner, o_status = Profile().get_one_verified_info(asset['owners'][0].lower())
            #                 asset.update({'creatorDetails': creator, 'ownerDetails': owner})
            #                 output_items.append(asset)
            #         except Exception:
            #             self.logger.error(f"Something went wrong")
            #     return {'items': output_items}, 200
            output = {}
            output['offset'] = offset
            output['limit'] = limit
            output['items'] = list(self.collection
                            .find(find_query, {'_id': 0})
                            .sort(sort_query)
                            .skip(int(offset))
                            .limit(int(limit)))

            for asset in output['items']:
                try:
                    creator, c_status = Profile().get_one_verified_info(asset['creator'].lower())
                    owner, o_status = Profile().get_one_verified_info(asset['owners'][0].lower())
                    asset.update({'creatorDetails': creator, 'ownerDetails': owner})
                except Exception:
                    self.logger.error(f"Something went wrong")
            
            return output, 200
        except Exception:
            return {
                "error": f"Something went wrong while filtering data, Exception : {traceback.format_exc()}"
            }, 503

    def get_all(self, creator=None, owner=None, status=None, limit=None, offset=None,onSale=None):
        """ Get all assets """
        query = {}
        output = {}
        if creator:
            query['creator'] = {'$regex': creator, '$options': 'i'}
        if owner:
            query['owners'] = {'$regex': owner, '$options': 'i'}
        if status:
            query['status'] = {'$regex': status, '$options': 'i'}
            query['listed'] = {'$ne': False}
        if onSale:
            query['onSale']= {'$ne': not onSale}
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
                creator, c_status = Profile().get_one_verified_info(asset['creator'].lower())
                owner, o_status = Profile().get_one_verified_info(asset['owners'][0].lower())
                asset.update({'creatorDetails': creator, 'ownerDetails': owner})
            except Exception:
                self.logger.error(f"Something went wrong")

        return output, 200

    
    def get_count(self, creator=None, owner=None, status=None):
        """ Get count of """
        query = {}
        if creator:
            query['creator'] = {'$regex': creator, '$options': 'i'}
        if owner:
            query['owners'] = {'$regex': owner, '$options': 'i'}
        if status:
            query['status'] = {'$regex': status, '$options': 'i'}

        output = self.collection.find(query, {'_id': 0}).count()
            
        return {"count": output}, 200


    def get_nft_count_from_collection(self,collectionId=None):
        query={}
        if collectionId:
            query['collectionId']={'$regex': collectionId, '$options': 'i'}
        output= self.collection.find(query,{'_id': 0}).count() 
        return output,200
    def get_nft_list_from_collection(self,collectionId=None,limit=None, offset=None):
        query={}
        output={}
        if collectionId:
            query={'collectionId':collectionId} 
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
        return output,200              
    def get_one(self, assetId):
        """ Return a assets """
        item = self.collection.find_one({'id': assetId}, {'_id': 0})

        try:
            creator, c_status = Profile().get_one_verified_info(item['creator'].lower())
            owner, o_status = Profile().get_one_verified_info(item['owners'][0].lower())
            item.update({'creatorDetails': creator, 'ownerDetails': owner})
        except Exception:
            self.logger.error(f"Something went wrong while fetching owner and creator for assetId: {assetId}")

        if item:
            self.logger.info(f"Asset {assetId} found")
            return item, 200

        self.logger.info(f"Asset {assetId} not found")
        return {
            'error': f"Asset {assetId} not found"
        }, 400


    def get_username(self, address):
        """ Get a user"""
        resp, code = Profile().get_one(address)
        if code == 200:
            return resp['userName']
        else:
            return ""

    
    def create_one(self, data):
        """ Create a asset """
        get_one = self.get_one(data['id'])
        if get_one[1] == 200:
            return {
                'error': f"Asset {data['id']} already exists"
            }, 409

        data['creatorUsername'] = self.get_username(data['creator'])
        data['ownerUsername'] = [self.get_username(data['owners'][0])]

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
            self.logger.info(f"Asset {assetId} updated")
        return {
            'error': f'Asset {assetId} not found'
        }, 404
    def latest_image_assets(self,limit=None, offset=None):
        find_query = {
                    'status': 'success',
                    'listed': {'$ne': False},
                    '$or': [
                            {'meta.type': 'image/png'},
                            {'meta.type':  'image/gif'},
                            {'meta.type': 'image/jpeg'}
                        ]
                    }
        output = {}        
        if offset and limit:
            output['offset'] = offset
            output['limit'] = limit
            output['items'] = list(self.collection
                                    .find(find_query, {'_id': 0,'item.image':1,'meta.type':1})
                                    .sort('_id', -1)
                                    .skip(int(offset))
                                    .limit(int(limit)))
        else:
            output['items'] = list(self.collection.find(find_query, {'_id': 0}).sort('_id', -1))

        return output, 200