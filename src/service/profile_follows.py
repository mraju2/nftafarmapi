""" Asset Likes and Views Service """
from pymongo.errors import DuplicateKeyError
from settings import USE_MONGO
from service.service_base import ServiceBase
from service.profile import Profile
from service.web3 import Web3Alley
import traceback


class ProfileFollows(ServiceBase):
    """ Asset Likes and Views Service """        

    def update_follow(self, data):
        """ Update like in asset """
        try:
            item, status = self.get_one(data['address'])
            request_payload = item if status == 200 else {"address": data['address'], "following": [], "followingCount" : 0,"follower":[],"followerCount":0}
            followerItem,followerStatus=self.get_one(data['followingAddress'])
            follower_req_payload= followerItem if followerStatus == 200 else {"address":data['followingAddress'],"follower":[],"followerCount":0,"following": [], "followingCount" : 0} 
            if data['follow'] is True:
                request_payload['following'].append(data['followingAddress'])
                request_payload['followingCount'] += 1
                follower_req_payload["follower"].append(data['address'])
                follower_req_payload['followerCount'] += 1
                
            elif data['follow'] is False:
                request_payload['following'].remove(data['followingAddress'])
                request_payload['followingCount'] -= 1
                follower_req_payload['follower'].remove(data['address'])
                follower_req_payload['followerCount'] -= 1
            if data['follow']:    
                msg = f"You are about to Follow profile: {data['address']}"
            else:
                msg = f"You are about to Unfollow profile: {data['address']}"   
             
            if status == 200 :
                signed_owner = Web3Alley().read_sign(msg, data['sign'])
                if signed_owner.lower() != item['address'].lower():
                    self.logger.error(f"Profile_Follow method: Not a trusted request {data['address']}")
                    return {"error": "Not a trusted request"}, 400   
                self.update_one(data['address'], request_payload)
            else:
                self.create_one(request_payload)
        
            if  followerStatus == 200:
                self.update_one(data['followingAddress'],follower_req_payload)
            else:
                self.create_one(follower_req_payload)
            Profile().update_one(data['address'], {'followingCount': request_payload['followingCount']})    
            Profile().update_one(data['followingAddress'], {'followerCount':follower_req_payload['followerCount']})         
            self.logger.info(f"profile following method: Following completed successfully for {data['address']}.")
            self.logger.info(f"profile follower method: Follower completed successfully for {data['followingAddress']}.")
            return {"message": f"Follows updated successfully for {data['address']}"}, 200
           
        except Exception:
            self.logger.error(f"Failure in Follower method for {data['followingAddress']}, Exception : {traceback.format_exc()}")
            return {
                "error": f"Something went wrong, Exception :"
            }, 503

    
    def get_one(self, address):
        """ Return a assetLike entry """
        item = self.collection.find_one({'address': address}, {'_id': 0})

        if item:
            return item, 200

        return {
            'error': f"Profile {address} not found"
        }, 400

    def get_following_profiles(self, address):
        """ Return follow address for user """
        items = list(self.collection.find({'address': address}, {'following': 1,'follower':1,'_id': 0}))
        FollowingIds = [item['following'] for item in items]
        FollowerIds=   [item['follower'] for item in items]
        self.logger.info(f"profile follower and following list method: follower and following completed successfully for {address}.")
        return {"Followinglist": FollowingIds,"FollowerList":FollowerIds}, 200
    
    def create_one(self, data):
        """ Create a Follow """
        get_one = self.get_one(data['address'])
        if get_one[1] == 200:
            return {
                'error': f"Profile {data['address']} already exists"
            }, 409

        # Create document
        try:
            self.collection.insert_one(data)
        except DuplicateKeyError:
            return {
                'error': f"Profile Follow {data['address']} already exists"
            }, 409

        if '_id' in data:
            del data['_id']
        # created successfully
        return {
            'message': f"Profile {data['address']} created successfully",
            'data': data
        }, 201
        

    def update_one(self, address, data):
        """ Update a Profile Follow entry """

        # pylint: disable=len-as-condition
        result = self.collection.update_one(
            {'address': address},
            {'$set': data})
        if result.matched_count:
            if result.modified_count:
                return {
                    'message': f'Follow {address} changed',
                    'data': data
                }, 200
            return {
                'message': f'Follow {address} updated',
                'data': data
            }, 200
        return {
            'error': f'Follow {address} not found'
        }, 404

    def delete_one(self, address):
        """ Delete a Profile Follow entry """
        result = self.collection.delete_one({'address': address})
        if result.deleted_count:
            return {
                'message': f'Follow {address} deleted'
            }, 200

        return {
            'error': f'Follow profile {address} not found'
        }, 404
