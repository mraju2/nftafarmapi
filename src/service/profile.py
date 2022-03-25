""" Profile Service """
from pymongo.errors import DuplicateKeyError
from settings import USE_MONGO
from service.service_base import ServiceBase
from service.web3 import Web3Alley
import traceback


class Profile(ServiceBase):
    """ Profile Service """

    def search_profiles(self, search_text, limit=None):
        """ Search profiles """
        query = {
            '$or': [
                        {'address': {'$regex': '.*'+ search_text + '.*', '$options': 'i'}},
                        {'userName': {'$regex': '.*'+ search_text + '.*', '$options': 'i'}},
                        {'email': {'$regex': '.*'+ search_text + '.*', '$options': 'i'}},
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

    def get_all_verified_addresses(self):
        """ Get all profiles """
        output = list(self.collection
                                    .find({'verified': True}, {'_id': 0, 'address': 1})
                                    .sort('_id', -1))
        addresses = [i['address'] for i in output]
        return addresses
    
    def get_all(self, verified=None, limit=None, offset=None):
        """ Get all profiles """
        query = {}
        output = {}
        
        if verified != None:
            if verified:
                query['verified'] = True
            else:
                query['verified'] = {'$ne': True}

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
        return output, 200


    def get_one(self, address):
        """ Return a profile """
        item = self.collection.find_one({'address': {'$regex': address, '$options': 'i'}}, {'_id': 0})

        if item:
            return item, 200

        return {
            'error': f"Profile {address} not found"
        }, 400


    def get_one_verified_info(self, address):
        """ Return a profile """
        item = self.collection.find_one({'address': {'$regex': address, '$options': 'i'}}, {'_id': 0, 'address': 1, 'verified': 1})

        if item:
            return item, 200

        return {
            'error': f"Profile {address} not found"
        }, 400


    def create_one(self, data):
        """ Create a profile """
        get_one = self.get_one(data['address'])
        if get_one[1] == 200:
            self.logger.error(f"Profile {data['address']} already exists")
            return {
                'error': f"Profile {data['address']} already exists"
            }, 409

        # Create document
        try:
            data['address'] = data['address'].lower()
            self.collection.insert_one(data)
            self.logger.info(f"Profile {data['address']}created")
        except DuplicateKeyError:
            self.logger.error(f"Profile {data['address']} already exists")
            return {
                'error': f"Profile {data['address']} already exists"
            }, 409

        if '_id' in data:
            del data['_id']
        # created successfully
        return {
            'message': f"Profile {data['address']} created successfully",
            'data': data
        }, 201

    def delete_one(self, address):
        """ Delete a profile """
        result = self.collection.delete_one({'address': address})
        if result.deleted_count:
            return {
                'message': f'Profile {address} deleted'
            }, 200

        return {
            'error': f'Profile {address} not found'
        }, 404
        

    def update_one(self, address, data):
        """ Update a profile """

        # pylint: disable=len-as-condition
        result = self.collection.update_one(
            {'address': address},
            {'$set': data})
        if result.matched_count:
            if result.modified_count:
                return {
                    'message': f'Profile {address} changed',
                    'data': data
                }, 200
            return {
                'message': f'Profile {address} updated',
                'data': data
            }, 200
        return {
            'error': f'Profile {address} not found'
        }, 404


    def update_profile(self, address, data):
        """ Update a profile """

        profile, profile_status_code = self.get_one(address)
        if profile_status_code != 200:
            self.logger.error(f"Profile {address} is not found")
            return profile, profile_status_code

        # msg = ""
        # signed_owner = Web3Alley().decode_sign(msg, data['sign'])
        # if signed_owner.lower() != address.lower():
        #     return {"error": "Not a trusted request"}, 400

        # payload = {'sign': data['sign']}
        payload = {}
        if 'userName' in data:
            payload['userName'] = data['userName']
        if 'description' in data:
            payload['description'] = data['description']
        if 'twitterId' in data:
            payload['twitterId'] = data['twitterId']
        if 'ownedSite' in data:
            payload['ownedSite'] = data['ownedSite']
        if 'instagramId' in data:
            payload['instagramId']=data['instagramId']
        if 'image' in data:
            payload['image'] = data['image']

        result = self.collection.update_one(
            {'address': address},
            {'$set': payload})
        if result.matched_count:
            if result.modified_count:
                return {
                    'message': f'Profile {address} changed',
                }, 200
            return {
                'message': f'Profile {address} updated',
            }, 200
            self.logger.info(f"Profile {address} updated")
        self.logger.error(f"Profile {address} not found")    
        return {
            'error': f'Profile {address} not found'
        }, 404

    
    def verify_profile(self, data):
        """ List or Delist an Asset """
        try:
            profile, profile_status_code = self.get_one(data['address'])
            if profile_status_code != 200:
                return profile, profile_status_code

            response = self.update_one(data['address'], {'verified': data['verified']})
            
            return response
        except Exception:
            self.logger.error(f"Failure in list_asset method for {data['address']}, Exception : {traceback.format_exc()}")
            return {
                "error": f"Something went wrong with the verification confirmation"
            }, 503

    