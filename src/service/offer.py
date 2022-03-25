""" Offer Service """
from pymongo.errors import DuplicateKeyError
from settings import USE_MONGO
from service.service_base import ServiceBase
from service.config import Config
from service.asset import Asset
from service.web3 import Web3, Web3Alley
import uuid
from datetime import datetime, timezone
from settings import BLOCK_CHAIN
from util.utils import get_sort_by_priceUnit

class Offer(ServiceBase):
    """ Offer Service """

    def get_all(self, assetId=None, user=None):
        """ Get all offers """
        query = {}
        if assetId:
            query['assetId'] = {'$regex': assetId, '$options': 'i'}
        if user:
            query.update({
                '$or': [
                    
                    {'bidder': {'$regex': user, '$options': 'i'}}
                ]
            })
        items = list(self.collection.find(query, {'_id': 0}))
        items.reverse()
        return {
            'items': items
        }, 200


    def get_one(self, offerId):
        """ Return a offers """
        item = self.collection.find_one({'id': offerId}, {'_id': 0})

        if item:
            return item, 200

        return {
            'error': f"Offer {offerId} not found"
        }, 400


    def create_one(self, data):
        """ Create a offer """
        get_one = self.get_one(data['id'])
        if get_one[1] == 200:
            return {
                'error': f"Offer {data['id']} already exists"
            }, 409

        asset_offers, status_code = self.get_all(assetId=data['assetId'])
        ids = []
        for item in asset_offers['items']:
            if item['priceUnit'] == data['priceUnit'] and item['status'] == "active":
                ids.append(item['id'])

        # Create document
        try:
            self.collection.insert_one(data)
        except DuplicateKeyError:
            return {
                'error': f"Offer {data['id']} already exists"
            }, 409
        except Exception as ex:
            return {
                'error': f"Error occured while creating offer {data['id']} : {ex}"
            }, 503

        for i in ids:
            self.update_one(i, {"status": "void"})

        if '_id' in data:
            del data['_id']

        Asset().update_one(data['assetId'], {f"highestBid{data['priceUnit']}": data['price'], "bidStatus": "active"})
        # created successfully
        return {
            'message': f"Offer {data['id']} created successfully",
            'data': data
        }, 201

    def delete_one(self, offerId):
        """ Delete a Offer """
        result = self.collection.delete_one({'id': offerId})
        if result.deleted_count:
            return {
                'message': f'Offer {offerId} deleted'
            }, 200

        return {
            'error': f'Offer {offerId} not found'
        }, 404
        

    def update_one(self, offerId, data):
        """ Update a Offer """

        # pylint: disable=len-as-condition
        result = self.collection.update_one(
            {'id': offerId},
            {'$set': data})
        if result.matched_count:
            if result.modified_count:
                return {
                    'message': f'Offer {offerId} changed',
                    'data': data
                }, 200
            return {
                'message': f'Offer {offerId} updated',
                'data': data
            }, 200
        return {
            'error': f'Offer {offerId} not found'
        }, 404

    def update_asset_offers(self, assetId, offerId=None):
        """ Update Offers for asset """

        asset_offers, status_code = self.get_all(assetId=assetId)
        ids = []
        for item in asset_offers['items']:
            if item['status'] == "active":
                ids.append(item['id'])

        for i in ids:
            if offerId and offerId == i:
                self.update_one(i, {"status": "accepted"})
            else:
                self.update_one(i, {"status": "void"})

    def cancel_bid(self, data):
        """ cancel bid for asset """

        offer, offer_status_code = self.get_one(data['bidId'])
        if offer_status_code != 200:
            return offer, offer_status_code
        address = offer['assetId'].split(":")[0]
        signed_owner = Web3Alley().decode_sign(address, offer['price'], data['sign'])
        if signed_owner.lower() != offer['bidder'].lower():
            return {"error": "Not a trusted request"}, 400

        self.update_one(data['bidId'], {"status": "cancelled"})

        asset_offers, asset_status_code = self.get_all(assetId=offer['assetId'])
        ids = []
        for item in asset_offers['items']:
            if item['status'] == "active":
                ids.append(item['id'])

        if not ids:
            Asset().update_one(offer['assetId'], {"bidStatus": "void"})
        
        return {"message": "Bid cancelled successfully"}, 200

    # def cancel_bid(self, data):
    #     """ cancel bid for asset """

    #     offer, offer_status_code = self.get_one(data['bidId'])
    #     if offer_status_code != 200:
    #         return offer, offer_status_code
    #     address = offer['assetId'].split(":")[0]
    #     signed_owner = Web3Alley().decode_sign(address, offer['price'], data['sign'])
    #     if signed_owner.lower() != offer['bidder'].lower():
    #         return {"error": "Not a trusted request"}, 400

    #     self.update_one(data['bidId'], {"status": "cancelled"})

    #     asset_offers, asset_status_code = self.get_all(assetId=offer['assetId'])
    #     ids = []
    #     for item in asset_offers['items']:
    #         if item['status'] == "active":
    #             ids.append(item['id'])

    #     if not ids:
    #         #Asset().update_one(offer['assetId'], {"bidStatus": "void"})
    #         itemsAlley=[]
    #         itemsWBid=[]
    #         for item in asset_offers['items']:
    #             if item['status'] == 'cancelled' and item['priceUnit']=="ALLEY" :
    #                 itemsAlley.append(item)
    #             elif item['status'] == 'cancelled' and item['priceUnit']==f"w{BLOCK_CHAIN}" :
    #                 itemsWBid.append(item)
    #         if(len(itemsAlley)==1):
    #             itemsAlley.sort(key=get_sort_by_priceUnit)
    #             print(itemsAlley)
    #             self.update_one(itemsAlley[-1]['id'], {"status": "active"})
    #         elif(len(itemsAlley)>=2):
    #             itemsAlley.sort(key=get_sort_by_priceUnit)
    #             print(itemsAlley)
    #             self.update_one(itemsAlley[-2]['id'], {"status": "active"})    
    #         elif (len(itemsWBid)==1):
    #             itemsAlley.sort(key=get_sort_by_priceUnit) 
    #             print(itemsWBid[-1]) 
    #             self.update_one(itemsWBid[-1]['id'], {"status": "active"})
    #         elif (len(itemsWBid)>=2):
    #             itemsAlley.sort(key=get_sort_by_priceUnit)
    #             print(itemsWBid[-2]) 
    #             self.update_one(itemsAlley[-2]['id'], {"status": "active"})    
    #         else:
    #             Asset().update_one(offer['assetId'], {"bidStatus": "void"})

    #     return {"message": "Bid cancelled successfully"}, 200


    def place_bid(self, data):
        """ Place a bid """

        asset, asset_status_code = Asset().get_one(data['assetId'])
        if asset_status_code != 200:
            return asset, asset_status_code
        address = asset['id'].split(":")[0]
        signed_owner = Web3Alley().decode_sign(address, data['price'], data['sign'])
        if signed_owner.lower() != data['bidder'].lower():
            return {"error": "Not a trusted request"}, 400

        asset_offers, status_code = self.get_all(assetId=data['assetId'])
        for item in asset_offers['items']:
            if item['priceUnit'] == data['priceUnit'] and item['price'] >= data['price'] and item['status'] == "active":
                return {'error': "Offer not valid"}, 400

        # ids = []
        # for item in asset_offers['items']:
        #     if item['priceUnit'] == data['priceUnit'] and item['status'] == "active":
        #         ids.append(item['id'])

        # Create document
        payload = {
            "id": str(uuid.uuid4()),
            "assetId": asset['id'],
            "token": asset['token'],
            "tokenId": asset['tokenId'],
            "owner": asset['owners'][0],
            "value": asset['value'],
            "price": data['price'],
            "priceUnit": data['priceUnit'],
            "bidder": data['bidder'].lower(),
            "status": "active",
            "date": str(datetime.now(timezone.utc).timestamp()),
            "sign": data['sign'],
        }
        try:
            self.collection.insert_one(payload)
            self.logger.info(f"placed a bid on Asset {payload['assetId']} and sign {payload['sign']}")
        except DuplicateKeyError:
            return {
                'error': f"Offer {payload['id']} already exists"
            }, 409
        except Exception as ex:
            return {
                'error': f"Error occured while creating offer {payload['id']} : {ex}"
            }, 503

        # for i in ids:
        #     self.update_one(i, {"status": "void"})

        if '_id' in payload:
            del payload['_id']

        Asset().update_one(data['assetId'], {f"highestBid{data['priceUnit']}": data['price'], "bidStatus": "active"})
        # created successfully
        return {
            'message': f"Offer created successfully",
        }, 201

        