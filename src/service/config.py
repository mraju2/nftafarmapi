""" Config Service """
from pymongo.errors import DuplicateKeyError
from settings import USE_MONGO
from service.service_base import ServiceBase


class Config(ServiceBase):
    """ Config Service """

    def get_all(self):
        """ Get all configs """
        items = list(self.collection.find({}, {'_id': 0}))
        return {
            'items': items
        }, 200


    def get_one(self, name):
        """ Return a configs """
        item = self.collection.find_one({'name': name}, {'_id': 0})

        if item:
            return item, 200

        return {
            'error': f"Config {name} not found"
        }, 400


    def create_one(self, data):
        """ Create a config """

        # Set key to name
        data['_id'] = data['name']

        # Create document
        try:
            self.collection.insert_one(data)
        except DuplicateKeyError:
            return {
                'error': f"Config {data['name']} already exists"
            }, 409

        # created successfully
        return {
            'message': f"Config {data['name']} created successfully",
            'data': data
        }, 201

    def delete_one(self, name):
        """ Delete a Config """
        result = self.collection.delete_one({'name': name})
        if result.deleted_count:
            return {
                'message': f'Config {name} deleted'
            }, 200

        return {
            'error': f'Config {name} not found'
        }, 404
        

    def update_one(self, name, data):
        """ Update a Config """
        
        if data['token'] != "NfTAlley@!7":
            return {"error": "Not Authorized"}, 401
        del data['token']
        # pylint: disable=len-as-condition
        result = self.collection.update_one(
            {'name': name},
            {'$set': data})
        if result.matched_count:
            if result.modified_count:
                return {
                    'message': f'Config {name} changed',
                    'data': {'name': name, 'value': data['value']}
                }, 200
            return {
                'message': f'Config {name} updated',
                'data': {'name': name, 'value': data['value']}
            }, 200
            self.logger.info(f"config {name} updated")
        return {
            'error': f'Config {name} not found'
        }, 404
