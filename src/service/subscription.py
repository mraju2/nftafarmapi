""" Subscription Service """
from pymongo.errors import DuplicateKeyError
from settings import USE_MONGO
from service.service_base import ServiceBase


class Subscription(ServiceBase):
    """ Subscription Service """

    def get_all(self):
        """ Get all subscribed emails """
        items = list(self.collection.find({}, {'_id': 0}))
        return {
            'items': items
        }, 200


    def get_one(self, email):
        """ Return a subscribed email """
        item = self.collection.find_one({'email': {'$regex': email, '$options': 'i'}}, {'_id': 0})

        if item:
            return item, 200

        return {
            'error': f"Subscription {email} not found"
        }, 400


    def create_one(self, data):
        """ Create a subscription """
        get_one = self.get_one(data['email'])
        if get_one[1] == 200:
            return {
                'error': f"Subscription {data['email']} already exists"
            }, 409

        # Create document
        try:
            self.collection.insert_one({'email': data['email']})
        except DuplicateKeyError:
            return {
                'error': f"Subscription {data['email']} already exists"
            }, 409

        if '_id' in data:
            del data['_id']
        # created successfully
        return {
            'message': f"Subscription {data['email']} created successfully",
        }, 201

    def delete_one(self, email):
        """ Delete a Subscription """
        result = self.collection.delete_one({'email': email})
        if result.deleted_count:
            return {
                'message': f'Subscription {email} deleted'
            }, 200

        return {
            'error': f'Subscription {email} not found'
        }, 404
        

    # def update_one(self, name, data):
    #     """ Update a Config """

    #     # pylint: disable=len-as-condition
    #     result = self.collection.update_one(
    #         {'name': name},
    #         {'$set': data})
    #     if result.matched_count:
    #         if result.modified_count:
    #             return {
    #                 'message': f'Config {name} changed',
    #                 'data': data
    #             }, 200
    #         return {
    #             'message': f'Config {name} updated',
    #             'data': data
    #         }, 200
    #     return {
    #         'error': f'Config {name} not found'
    #     }, 404
