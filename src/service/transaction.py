""" Transaction Service """
from pymongo.errors import DuplicateKeyError
from settings import USE_MONGO
from service.service_base import ServiceBase
from service.config import Config
from service.asset import Asset
from service.offer import Offer
from service.asset_archived import AssetArchived
from service.web3 import Web3Alley
import traceback
import uuid
from datetime import datetime, timezone
import requests
# from flask_socketio import emit

class Transaction(ServiceBase):
    """ Transaction Service """

    def get_all(self, assetId=None, user=None):
        """ Get all transactions """
        query = {'status': {'$ne': 'failed'}}
        if assetId:
            query['assetId'] = {'$regex': assetId, '$options': 'i'}
        if user:
            query.update({
                '$or': [
                    {'to': {'$regex': user, '$options': 'i'}},
                    {'from': {'$regex': user, '$options': 'i'}},
                    {'buyer': {'$regex': user, '$options': 'i'}},
                    {'owner': {'$regex': user, '$options': 'i'}},
                ]
            })
        items = list(self.collection.find(query, {'_id': 0}))
        items.reverse()
        return {
            'items': items
        }, 200


    def get_all_failed(self, assetId=None, user=None):
        """ Get all transactions """
        query = {'status': 'failed'}
        if assetId:
            query['assetId'] = {'$regex': assetId, '$options': 'i'}
        if user:
            query.update({
                '$or': [
                    {'to': {'$regex': user, '$options': 'i'}},
                    {'from': {'$regex': user, '$options': 'i'}},
                    {'buyer': {'$regex': user, '$options': 'i'}},
                    {'owner': {'$regex': user, '$options': 'i'}},
                ]
            })
        items = list(self.collection.find(query, {'_id': 0}))
        items.reverse()
        return {
            'items': items
        }, 200


    def get_one(self, transactionId):
        """ Return a transactions """
        item = self.collection.find_one({'id': transactionId}, {'_id': 0})

        if item:
            return item, 200

        return {
            'error': f"Transaction {transactionId} not found"
        }, 400


    def create_one(self, data):
        """ Create a transaction """
        get_one = self.get_one(data['id'])
        if get_one[1] == 200:
            return {
                'error': f"Transaction {data['id']} already exists"
            }, 409

        if data['type'] == 'buy':
            serviceCharge = Config().get_one(f"SERVICE_CHARGE_{data['priceUnit']}")[0]['value']
            royalty = Asset().get_one(data['assetId'])[0]['royalty']
            data['serviceShare'] = data['price'] * float(serviceCharge)/100
            data['creatorShare'] = (data['price'] - data['serviceShare'])* int(royalty)/100 
            data['ownerShare'] = data['price'] - data['creatorShare']
            
        # Create document
        try:
            self.collection.insert_one(data)
        except DuplicateKeyError:
            return {
                'error': f"Transaction {data['id']} already exists"
            }, 409

        if '_id' in data:
            del data['_id']

        # created successfully
        return {
            'message': f"Transaction {data['id']} created successfully",
            'data': data
        }, 201

    def delete_one(self, transactionId):
        """ Delete a Transaction """
        result = self.collection.delete_one({'id': transactionId})
        if result.deleted_count:
            return {
                'message': f'Transaction {transactionId} deleted'
            }, 200

        return {
            'error': f'Transaction {transactionId} not found'
        }, 404
        

    def update_one(self, transactionId, data):
        """ Update a Transaction """

        # pylint: disable=len-as-condition
        result = self.collection.update_one(
            {'id': transactionId},
            {'$set': data})
        if result.matched_count:
            if result.modified_count:
                return {
                    'message': f'Transaction {transactionId} changed',
                    'data': data
                }, 200
            return {
                'message': f'Transaction {transactionId} updated',
                'data': data
            }, 200
        return {
            'error': f'Transaction {transactionId} not found'
        }, 404

    
    def process_transaction(self, data):
        """ Complete Transaction Process """
        try:
            if data["type"] == "buy":
                asset_data = {
                    "owners": data["owners"],
                    "onSale": data["onSale"],
                    "status": data["status"],
                    "bidStatus": "void",
                    "lastTransactionStatus": data['lastTransactionStatus']
                }
                buy_transaction_data = {
                    "type": data["type"],
                    "id": data["id"],
                    "assetId": data["assetId"],
                    "token": data["token"],
                    "tokenId": data["tokenId"],
                    "owner": data["owner"],
                    "creator": data["creator"],
                    "value": data["value"],
                    "price": data["price"],
                    "priceUnit": data["priceUnit"],
                    "date": data["date"],
                    "transactionHash": data["transactionHash"],
                    "buyer": data["buyer"],
                    "from": data["from"],
                    "to": data["to"],
                }
                Asset().update_one(data["assetId"], asset_data)
                self.create_one(buy_transaction_data)
                Offer().update_asset_offers(assetId=data["assetId"])

            elif data["type"] == "transfer":
                asset_data = {
                    "owners": data["owners"],
                    "onSale": data["onSale"],
                    "status": data["status"],
                    "bidStatus": "void",
                    "lastTransactionStatus": data['lastTransactionStatus']
                }
                transfer_transaction_data = {
                    "type": data["type"],
                    "id": data["id"],
                    "assetId": data["assetId"],
                    "token": data["token"],
                    "tokenId": data["tokenId"],
                    "owner": data["owner"],
                    "creator": data["creator"],
                    "value": data["value"],
                    "date": data["date"],
                    "transactionHash": data["transactionHash"],
                    "from": data["from"],
                    "to": data["to"],
                }
                Asset().update_one(data["assetId"], asset_data)
                self.create_one(transfer_transaction_data)

            elif data["type"] == "mint":
                asset_data = {
                    "id": data["assetId"],
                    "token": data["token"],
                    "tokenId": data["tokenId"],
                    "owners": data["owners"],
                    "onSale": data["onSale"],
                    "status": data["status"],
                    "mintTime": data["date"],
                    "lastTransactionStatus": data['lastTransactionStatus']
                }
                mint_transaction_data = {
                    "type": data["type"],
                    "id": data["id"],
                    "assetId": data["assetId"],
                    "token": data["token"],
                    "tokenId": data["tokenId"],
                    "owner": data["owner"],
                    "creator": data["creator"],
                    "value": data["value"],
                    "date": data["date"],
                    "transactionHash": data["transactionHash"],
                    "from": data["from"],
                    "to": data["to"],
                }
                Asset().update_one(data["transactionHash"], asset_data)
                self.create_one(mint_transaction_data)
                if data["onSale"]:
                    order_transaction_data = {
                        "type": "order",
                        "id": data["onSaleId"],
                        "assetId": data["assetId"],
                        "token": data["token"],
                        "tokenId": data["tokenId"],
                        "owner": data["owner"],
                        "creator": data["creator"],
                        "value": data["value"],
                        "price": data["price"],
                        "priceUnit": data["priceUnit"],
                        "date": data["date"],
                        "from": data["from"],
                    }
                    self.create_one(order_transaction_data)
            elif data["type"] == "bid":
                asset_data = {
                    "owners": data["owners"],
                    "onSale": data["onSale"],
                    "status": data["status"],
                    "bidStatus": "done",
                    "lastTransactionStatus": data['lastTransactionStatus']
                }
                bid_transaction_data = {
                    "type": data["type"],
                    "id": data["id"],
                    "assetId": data["assetId"],
                    "token": data["token"],
                    "tokenId": data["tokenId"],
                    "owner": data["owner"],
                    "creator": data["creator"],
                    "value": data["value"],
                    "price": data["price"],
                    "priceUnit": data["priceUnit"],
                    "date": data["date"],
                    "transactionHash": data["transactionHash"],
                    "buyer": data["buyer"],
                    "seller": data["seller"],
                    "from": data["from"],
                    "to": data["to"],
                }
                Asset().update_one(data["assetId"], asset_data)
                self.create_one(bid_transaction_data)
                Offer().update_asset_offers(assetId=data["assetId"], offerId=data["bidId"])
            return {
                "message": "Transaction processed successfully"
            }, 200
        except Exception:
            return {
                "error": f"Something went wrong, Exception : {traceback.format_exc()}"
            }, 503

    def process_failed_transaction(self, data):
        """ Complete Transaction Process """
        try:
            assetId = data['assetId']
            del data['assetId']
            Asset().update_one(assetId, data)
            return {
                "message": "Failed Transaction processed successfully"
            }, 200
        except Exception:
            return {
                "error": f"Something went wrong, Exception : {traceback.format_exc()}"
            }, 503

    def get_address(self, str):
        return f"0x{str[-40:]}".lower()
    
    def process_buy_transaction(self, data):
        """ process buy transaction """
        try:
            asset_resp, asset_status_code = Asset().get_one(data["assetId"])
            if asset_status_code != 200:
                raise Exception(f"process_buy_transaction method for assetId {data['assetId']} and hash {data['hash']}, error: {asset_resp}")
            Asset().update_one(data['assetId'], {'status': 'pending'})
            receipt_resp, receipt_status_code = Web3Alley().get_transaction_receipt(data['hash'])
            if receipt_status_code != 200:
                raise Exception(f"process_buy_transaction method for assetId {data['assetId']} and hash {data['hash']}, error: {receipt_resp}")
            if receipt_resp['status'] == 0:
                # failed transaction
                raise Exception(f"process_buy_transaction method: Transaction failed for {data['assetId']}. Transaction hash is {data['hash']}")
            elif receipt_resp['status'] == 1:
                # successful transaction
                try:
                    if receipt_resp['from'].lower() != data['buyer'].lower() and self.get_address(receipt_resp['logs'][1]['topics'][1]).lower() != asset_resp['owners'][0].lower():
                        raise Exception(f"process_buy_transaction method: Input payload details are not matching with blockchain transaction for {data['assetId']}.Transaction hash is {data['hash']}")
                except Exception:
                    raise Exception(f"process_buy_transaction method: Input payload details are not matching with blockchain transaction for {data['assetId']}.Transaction hash is {data['hash']}")
                epochtime = Web3Alley().get_block_time(receipt_resp['blockNumber'])
                asset_payload = {
                    "owners": [self.get_address(receipt_resp['logs'][1]['topics'][2])],
                    "onSale": False,
                    "status": "success",
                    "bidStatus": "void",
                    "lastTransactionStatus": "success"
                }
                buy_transaction_payload = {
                    "type": "buy",
                    "id": str(uuid.uuid4()),
                    "assetId": asset_resp["id"],
                    "token": asset_resp["token"],
                    "tokenId": asset_resp["tokenId"],
                    "owner": asset_resp["owners"][0],
                    "creator": asset_resp["creator"],
                    "value": asset_resp["value"],
                    "price": asset_resp["price"],
                    "priceUnit": asset_resp["priceUnit"],
                    "date": epochtime,
                    "transactionHash": data["hash"],
                    "buyer": self.get_address(receipt_resp['logs'][1]['topics'][2]),
                    "from": receipt_resp["from"],
                    "to": receipt_resp["to"],
                    }
                Asset().update_one(data["assetId"], asset_payload)
                self.create_one(buy_transaction_payload)
                Offer().update_asset_offers(assetId=data["assetId"])
                self.logger.info(f"process_buy_transaction method: Transaction completed successfully for {data['assetId']}.")
                # emit("buy", {'assetId': data['assetId'], 'hash': data['hash'],"status": "success"}, room=data['sid'], namespace="/notification")
                return {
                    "message": "Transaction completed successfully"
                }, 200
        except Exception as ex:
            try:
                self.logger.error(ex)
                self.logger.error(f"Failure in process_buy_transaction method for {data['assetId']},Transaction hash is {data['hash']}, Exception : {traceback.format_exc()}")
                asset_payload = {
                    "status": "success",
                    "lastTransactionStatus": "failed"
                }
                Asset().update_one(data['assetId'], asset_payload)
                failed_transaction_payload = {
                    "type": "buy",
                    "id": str(uuid.uuid4()),
                    "assetId": asset_resp["id"],
                    "owner": asset_resp["owners"][0],
                    "creator": asset_resp["creator"],
                    "value": asset_resp["value"],
                    "price": asset_resp["price"],
                    "priceUnit": asset_resp["priceUnit"],
                    "date": str(datetime.now(timezone.utc).timestamp()),
                    "transactionHash": data["hash"],
                    "buyer": data['buyer'].lower(),
                    "status": "failed",
                    "failureReason": str(ex)
                }
                self.create_one(failed_transaction_payload)
                # emit("buy", {'assetId': data['assetId'], 'hash': data['hash'], "status": "failed"}, room=data['sid'], namespace="/notification")
                return {
                        "error": f"Something went wrong with the transaction. Transaction hash is {data['hash']}"
                    }, 503
            except Exception:
                self.logger.error(f"Failure in process_buy_transaction method for {data['assetId']},Transaction hash is {data['hash']}, Exception : {traceback.format_exc()}")
                return {
                        "error": f"Something went wrong with the transaction. Transaction hash is {data['hash']}"
                    }, 503


    def process_transfer_transaction(self, data):
        """ process buy transaction """
        try:
            asset_resp, asset_status_code = Asset().get_one(data["assetId"])
            if asset_status_code != 200:
                raise Exception(f"process_transfer_transaction method for assetId {data['assetId']} and hash {data['hash']}, error: {asset_resp}")
            Asset().update_one(data['assetId'], {'status': 'pending'})
            receipt_resp, receipt_status_code = Web3Alley().get_transaction_receipt(data['hash'])
            if receipt_status_code != 200:
                raise Exception(f"process_transfer_transaction method for assetId {data['assetId']} and hash {data['hash']}, error: {receipt_resp}")
            if receipt_resp['status'] == 0:
                # failed transaction
                raise Exception(f"process_transfer_transaction method: Transaction failed for {data['assetId']}. Transaction hash is {data['hash']}")
            elif receipt_resp['status'] == 1:
                # successful transaction
                try:
                    if self.get_address(receipt_resp['logs'][1]['topics'][2]).lower() != data['to'].lower() and receipt_resp['from'].lower() != asset_resp['owners'][0].lower():
                        raise Exception(f"process_transfer_transaction method: Input payload details are not matching with blockchain transaction for {data['assetId']}.Transaction hash is {data['hash']}")
                except Exception:
                    raise Exception(f"process_transfer_transaction method: Input payload details are not matching with blockchain transaction for {data['assetId']}.Transaction hash is {data['hash']}")
                epochtime = Web3Alley().get_block_time(receipt_resp['blockNumber'])
                asset_payload = {
                    "owners": [self.get_address(receipt_resp['logs'][1]['topics'][2])],
                    "onSale": False,
                    "status": "success",
                    "bidStatus": "void",
                    "lastTransactionStatus": "success"
                }
                transfer_transaction_payload = {
                        "type": "transfer",
                        "id": str(uuid.uuid4()),
                        "assetId": asset_resp["id"],
                        "token": asset_resp["token"],
                        "tokenId": asset_resp["tokenId"],
                        "owner": self.get_address(receipt_resp['logs'][1]['topics'][2]),
                        "creator": asset_resp["creator"],
                        "value": asset_resp["value"],
                        "date": epochtime,
                        "transactionHash": data["hash"],
                        "from": receipt_resp["from"].lower(),
                        "to": receipt_resp["to"].lower(),
                    }
                Asset().update_one(data["assetId"], asset_payload)
                self.create_one(transfer_transaction_payload)
                Offer().update_asset_offers(assetId=data["assetId"])
                self.logger.info(f"process_transfer_transaction method: Transaction completed successfully for {data['assetId']}.")
                # emit("transfer", {'assetId': data['assetId'], 'hash': data['hash'], "status": "success"}, room=data['sid'], namespace="/notification")
                return {
                    "message": "Transaction completed successfully"
                }, 200
        except Exception as ex:
            try:
                self.logger.error(ex)
                self.logger.error(f"Failure in process_transfer_transaction method for {data['assetId']},Transaction hash is {data['hash']}, Exception : {traceback.format_exc()}")
                asset_payload = {
                    "status": "success",
                    "lastTransactionStatus": "failed"
                }
                Asset().update_one(data['assetId'], asset_payload)
                failed_transaction_payload = {
                    "type": "transfer",
                    "id": str(uuid.uuid4()),
                    "assetId": asset_resp["id"],
                    "owner": asset_resp["owners"][0],
                    "creator": asset_resp["creator"],
                    "value": asset_resp["value"],
                    "date": str(datetime.now(timezone.utc).timestamp()),
                    "transactionHash": data["hash"],
                    "to": data['to'],
                    "status": "failed",
                    "failureReason": str(ex)
                }
                self.create_one(failed_transaction_payload)
                # emit("transfer", {'assetId': data['assetId'], 'hash': data['hash'], "status": "failed"}, room=data['sid'], namespace="/notification")
                return {
                        "error": f"Something went wrong with the transaction. Transaction hash is {data['hash']}"
                    }, 503
            except Exception:
                self.logger.error(f"Failure in process_transfer_transaction method for {data['assetId']},Transaction hash is {data['hash']}, Exception : {traceback.format_exc()}")
                return {
                        "error": f"Something went wrong with the transaction. Transaction hash is {data['hash']}"
                    }, 503


    def process_bid_transaction(self, data):
        """ process bid transaction """
        try:
            bid_resp, bid_status_code = Offer().get_one(data["bidId"])
            if bid_status_code != 200:
                raise Exception(f"process_bid_transaction method: {bid_resp},AssetId {bid_resp['assetId']},Transaction hash is {data['hash']}")
            asset_resp, asset_status_code = Asset().get_one(bid_resp["assetId"])
            if asset_status_code != 200:
                raise Exception(f"process_bid_transaction method: {asset_resp},AssetId {bid_resp['assetId']},Transaction hash is {data['hash']}")
            Asset().update_one(bid_resp['assetId'], {'status': 'pending'})
            receipt_resp, receipt_status_code = Web3Alley().get_transaction_receipt(data['hash'])
            if receipt_status_code != 200:
                raise Exception(f"process_bid_transaction method: {receipt_resp},AssetId {bid_resp['assetId']},Transaction hash is {data['hash']}")
            if receipt_resp['status'] == 0:
                # failed transaction
                raise Exception(f"process_bid_transaction method: Transaction failed for {bid_resp['assetId']}.Transaction hash is {data['hash']}")
            elif receipt_resp['status'] == 1:
                # successful transaction
                try:
                    if self.get_address(receipt_resp['logs'][1]['topics'][2]).lower() != bid_resp['bidder'].lower() and receipt_resp['from'].lower() != asset_resp['owners'][0].lower():
                        raise Exception(f"process_bid_transaction method: Input payload details are not matching with blockchain transaction for {bid_resp['assetId']},Transaction hash is {data['hash']}")
                except Exception:
                    raise Exception(f"process_bid_transaction method: Input payload details are not matching with blockchain transaction for {bid_resp['assetId']},Transaction hash is {data['hash']}")
                epochtime = Web3Alley().get_block_time(receipt_resp['blockNumber'])
                asset_payload = {
                    "owners": [self.get_address(receipt_resp['logs'][1]['topics'][2])],
                    "onSale": False,
                    "status": "success",
                    "bidStatus": "done",
                    "lastTransactionStatus": "success"
                }
                bid_transaction_payload = {
                    "type": "bid",
                    "id": str(uuid.uuid4()),
                    "assetId": asset_resp["id"],
                    "token": asset_resp["token"],
                    "tokenId": asset_resp["tokenId"],
                    "owner": self.get_address(receipt_resp['logs'][1]['topics'][2]),
                    "creator": asset_resp["creator"],
                    "value": asset_resp["value"],
                    "price": bid_resp["price"],
                    "priceUnit": bid_resp["priceUnit"],
                    "date": epochtime,
                    "transactionHash": data["hash"],
                    "buyer": self.get_address(receipt_resp['logs'][1]['topics'][2]),
                    "seller": self.get_address(receipt_resp['logs'][1]['topics'][1]),
                    "from": receipt_resp["from"],
                    "to": receipt_resp["to"],
                    }
                Asset().update_one(bid_resp["assetId"], asset_payload)
                self.create_one(bid_transaction_payload)
                Offer().update_asset_offers(assetId=bid_resp["assetId"], offerId=data["bidId"])
                self.logger.info(f"process_bid_transaction method: Transaction completed successfully for {bid_resp['assetId']}, Hash is {data['hash']}")
                # emit("bid", {'assetId': bid_resp['assetId'], 'hash': data['hash'], "status": "success"}, room=data['sid'], namespace="/notification")
                return {
                    "message": "Transaction completed successfully"
                }, 200
        except Exception as ex:
            try:
                self.logger.error(ex)
                self.logger.error(f"Failure in process_bid_transaction method for {bid_resp['assetId']},Transaction hash is {data['hash']}, Exception : {traceback.format_exc()}")
                asset_payload = {
                    "status": "success",
                    "lastTransactionStatus": "failed"
                }
                Asset().update_one(bid_resp['assetId'], asset_payload)
                failed_transaction_payload = {
                    "type": "bid",
                    "id": str(uuid.uuid4()),
                    "assetId": asset_resp["id"],
                    "owner": asset_resp["owners"][0],
                    "creator": asset_resp["creator"],
                    "value": asset_resp["value"],
                    "date": str(datetime.now(timezone.utc).timestamp()),
                    "transactionHash": data["hash"],
                    "buyer": bid_resp['bidder'],
                    "seller": asset_resp["owners"][0],
                    "status": "failed",
                    "failureReason": str(ex)
                }
                self.create_one(failed_transaction_payload)
                # emit("bid", {'assetId': bid_resp['assetId'], 'hash': data['hash'], "status": "failed"}, room=data['sid'], namespace="/notification")
                return {
                        "error": f"Something went wrong with the transaction. Transaction hash is {data['hash']}"
                    }, 503
            except Exception:
                self.logger.error(f"Failure in process_bid_transaction method for {bid_resp['assetId']},Transaction hash is {data['hash']}, Exception : {traceback.format_exc()}")
                return {
                        "error": f"Something went wrong with the transaction. Transaction hash is {data['hash']}"
                    }, 503
    
    def update_asset(self, assetId, data):
        """ Update a Asset """

        asset, asset_status_code = Asset().get_one(assetId)
        if asset_status_code != 200:
            return asset, asset_status_code
        input = data['price'] if data['onSale'] else '0'
        address = asset['id'].split(":")[0]
        signed_owner = Web3Alley().decode_sign(address, input, data['sign'])
        if signed_owner.lower() != asset['owners'][0].lower():
            return {"error": "Not a trusted request"}, 400

        payload = {"sign": data['sign']}
        if data['onSale']:
            payload.update({
                'onSale': data['onSale'],
                'price': data['price'],
                'priceUnit': data['priceUnit']
            })
        else:
            payload.update({
                'onSale': data['onSale']
            })

        response = Asset().update_one(assetId, payload)

        if data['onSale']:
            trans_payload = {
                "type": "order",
                "id": str(uuid.uuid4()),
                "token": asset['token'],
                "assetId": asset['id'],
                "tokenId": asset['tokenId'],
                "owner": asset['owners'][0],
                "creator": asset['creator'],
                "value": asset['value'],
                "date": str(datetime.now(timezone.utc).timestamp()),
                "price": data['price'],
                "priceUnit": data['priceUnit'],
                "from": asset['owners'][0]
            }
            Transaction().create_one(trans_payload)
        else:
            trans_payload={
                "type": "offsale",
                "id": str(uuid.uuid4()),
                "token": asset['token'],
                "assetId": asset['id'],
                "tokenId": asset['tokenId'],
                "owner": asset['owners'][0],
                "creator": asset['creator'],
                "value": asset['value'],
                "date": str(datetime.now(timezone.utc).timestamp()),
                "from": asset['owners'][0]
            }
            Transaction().create_one(trans_payload)
        return response


    def process_mint_transaction(self, data):
        """ process mint transaction """
        try:
            asset_payload = {
                    "owners": [data['owners'][0]],
                    "onSale": data['onSale'],
                    "id": data['hash'],
                    "creator": data['creator'],
                    "categories": ["art"],
                    "meta": data['meta'],
                    "item": data['item'],
                    "royalty": data['royalty'],
                    "sign": data['sign'],
                    "status": "pending"
                }
            if data['onSale']:
                asset_payload['price'] = data['price']
                asset_payload['priceUnit'] = data['priceUnit']
            if "collectionId" in data:
                asset_payload['collectionId']=data['collectionId']    
            Asset().create_one(asset_payload)

            receipt_resp, receipt_status_code = Web3Alley().get_transaction_receipt(data['hash'])
            if receipt_status_code != 200:
                raise Exception(f"process_mint_transaction method: {receipt_resp},Transaction hash is {data['hash']}")
            if receipt_resp['status'] == 0:
                # failed transaction
                print("failed")
                asset_payload = {
                    "status": "failed",
                    "lastTransactionStatus": "failed"
                }
                Asset().update_one(data["hash"], asset_payload)
                raise Exception(f"process_mint_transaction method: Transaction failed for {data['hash']}. Transaction hash is {data['hash']}")
            elif receipt_resp['status'] == 1:
                # successful transaction
                epochtime = Web3Alley().get_block_time(receipt_resp['blockNumber'])
                tokenId = Web3Alley().convert_hex_to_number_string(receipt_resp['logs'][0]['topics'][3])
                update_asset_payload = {
                    "owners": [self.get_address(receipt_resp['logs'][0]['topics'][2])],
                    "onSale": data['onSale'],
                    "id": f"{receipt_resp['to'].lower()}:{tokenId}",
                    "tokenId": tokenId,
                    "token": receipt_resp['to'].lower(),
                    "value": 1,
                    "creator": data['creator'],
                    "categories": ["art"],
                    "mintTime": epochtime,
                    "meta": data['meta'],
                    "item": data['item'],
                    "royalty": data['royalty'],
                    "sign": data['sign'],
                    "status": "success",
                    "lastTransactionStatus": "success"
                }
                if data['onSale']:
                    update_asset_payload['price'] = data['price']
                    update_asset_payload['priceUnit'] = data['priceUnit']
                if "collectionId" in data:
                    update_asset_payload['collectionId'] = data['collectionId']

                mint_transaction_payload = {
                    "type": "mint",
                    "id": str(uuid.uuid4()),
                    "assetId": f"{receipt_resp['to'].lower()}:{tokenId}",
                    "token": receipt_resp['to'].lower(),
                    "tokenId": tokenId,
                    "owner": self.get_address(receipt_resp['logs'][0]['topics'][2]),
                    "creator": data["creator"],
                    "value": 1,
                    "date": epochtime,
                    "transactionHash": data["hash"],
                    "from": receipt_resp["from"].lower(),
                    "to": receipt_resp["to"].lower(),
                }
                if "collectionId" in data:
                    mint_transaction_payload['collectionId']=data['collectionId']

                Asset().update_one(data['hash'], update_asset_payload)
                self.create_one(mint_transaction_payload)
                if data['onSale']:
                    on_sale_payload = {
                        "type": "order",
                        "id": str(uuid.uuid4()),
                        "assetId": f"{receipt_resp['to'].lower()}:{tokenId}",
                        "token": receipt_resp['to'].lower(),
                        "tokenId": tokenId,
                        "owner": self.get_address(receipt_resp['logs'][0]['topics'][2]),
                        "creator": data["creator"],
                        "value": 1,
                        "price": data["price"],
                        "priceUnit": data["priceUnit"],
                        "date": epochtime,
                        "from": receipt_resp["from"].lower(),
                    }
                    self.create_one(on_sale_payload)
                self.logger.info(f"process_mint_transaction method: Transaction completed successfully for {data['hash']}")
                # emit("mint", {'assetId': f"{receipt_resp['to'].lower()}:{tokenId}", 'hash': data['hash'], "status": "success"}, room=data['sid'], namespace="/notification")
                return {
                    "message": "Transaction completed successfully"
                }, 200
        except Exception as ex:
            self.logger.error(ex)
            self.logger.error(f"Failure in process_mint_transaction method for {data['hash']}, Exception : {traceback.format_exc()}")
            asset_payload = {
                "status": "failed",
                "lastTransactionStatus": "failed"
            }
            Asset().update_one(data["hash"], asset_payload)
            # emit("mint", {'assetId': data['hash'], 'hash': data['hash'], "status": "failed"}, room=data['sid'], namespace="/notification")
            return {
                "error": f"Something went wrong with the transaction. Transaction hash is {data['hash']}"
            }, 503


    def list_asset(self, data):
        """ List or Delist an Asset """
        try:
            asset, asset_status_code = Asset().get_one(data['assetId'])
            if asset_status_code != 200:
                self.logger.error(f"list_asset method: {asset},assetId {data['assetId']},Transaction hash is {asset['hash']}")
                return asset, asset_status_code
            if data['listed']:    
                msg = f"You are about to List your nft: {data['assetId']}"
            else:
                msg = f"You are about to De-List your nft: {data['assetId']}"   
            signed_owner = Web3Alley().read_sign(msg, data['sign'])
            if signed_owner.lower() != asset['owners'][0].lower():
                self.logger.error(f"list_asset method: Not a trusted request {data['assetId']}")
                return {"error": "Not a trusted request"}, 400

            response = Asset().update_one(data['assetId'], {'listed': data['listed']})
            
            return response
        except Exception:
            self.logger.error(f"Failure in list_asset method for {data['assetId']},Transaction hash is {asset['hash']}, Exception : {traceback.format_exc()}")
            return {
                "error": f"Something went wrong with the process"
            }, 503

    
    def process_burn_transaction(self, data):
        """ process buy transaction """
        try:
            asset_resp, asset_status_code = Asset().get_one(data["assetId"])
            if asset_status_code != 200:
                raise Exception(f"process_burn_transaction method: {asset_resp},assetId is {data['assetId']},Transaction hash is {data['hash']}")
            Asset().update_one(data['assetId'], {'status': 'pending'})
            msg = f"You are about to Burn your nft: {data['assetId']}"   
            signed_owner = Web3Alley().read_sign(msg, data['sign'])
            if signed_owner.lower() != asset_resp['owners'][0].lower():
                raise Exception(f"process_burn_transaction method: Not a trusted request {data['assetId']} and hash is {data['hash']}")
            receipt_resp, receipt_status_code = Web3Alley().get_transaction_receipt(data['hash'])
            if receipt_status_code != 200:
                raise Exception(f"process_burn_transaction method: {receipt_resp}, assetId is {data['assetId']},Transaction hash is {data['hash']}")
            if receipt_resp['status'] == 0:
                # failed transaction
                raise Exception(f"process_burn_transaction method: Transaction failed for {data['assetId']}. Transaction hash is {data['hash']}")
            elif receipt_resp['status'] == 1:
                # successful transaction
                try:
                    if receipt_resp['from'].lower() != asset_resp['owners'][0].lower() and self.get_address(receipt_resp['logs'][1]['topics'][1]).lower() != asset_resp['owners'][0].lower():
                        raise Exception(f"process_burn_transaction method: Input payload details are not matching with blockchain transaction for {data['assetId']} and hash {data['hash']}")
                except Exception:
                    raise Exception(f"process_burn_transaction method: Input payload details are not matching with blockchain transaction for {data['assetId']} and hash {data['hash']}")
                self.unpin_pinata_image(asset_resp['item']['image'])
                epochtime = Web3Alley().get_block_time(receipt_resp['blockNumber'])
                asset_payload = {
                    "owners": [self.get_address(receipt_resp['logs'][1]['topics'][2])],
                    "onSale": False,
                    "status": "success",
                    "bidStatus": "void",
                    "lastTransactionStatus": "success"
                }
                burn_transaction_payload = {
                    "type": "burn",
                    "id": str(uuid.uuid4()),
                    "assetId": asset_resp["id"],
                    "token": asset_resp["token"],
                    "tokenId": asset_resp["tokenId"],
                    "owner": asset_resp["owners"][0],
                    "creator": asset_resp["creator"],
                    "value": asset_resp["value"],
                    "date": epochtime,
                    "transactionHash": data["hash"],
                    "from": receipt_resp["from"],
                    "to": receipt_resp["to"],
                    }
                self.create_one(burn_transaction_payload)
                Offer().update_asset_offers(assetId=data["assetId"])
                AssetArchived().create_one(asset_resp)
                Asset().delete_one(data['assetId'])
                self.logger.info(f"process_burn_transaction method: Transaction completed successfully for {data['assetId']} and hash {data['hash']}")
                # emit("burn", {'assetId': data["assetId"], 'hash': data['hash'], "status": "success"}, room=data['sid'], namespace="/notification")
                return {
                    "message": "Transaction completed successfully"
                }, 200
        except Exception as ex:
            try:
                self.logger.error(ex)
                self.logger.error(f"Failure in process_burn_transaction method for {data['assetId']} and hash {data['hash']}, Exception : {traceback.format_exc()}")
                asset_payload = {
                    "status": "success",
                    "lastTransactionStatus": "failed"
                }
                Asset().update_one(data['assetId'], asset_payload)
                failed_transaction_payload = {
                    "type": "burn",
                    "id": str(uuid.uuid4()),
                    "assetId": asset_resp["id"],
                    "owner": asset_resp["owners"][0],
                    "creator": asset_resp["creator"],
                    "value": asset_resp["value"],
                    "date": str(datetime.now(timezone.utc).timestamp()),
                    "transactionHash": data["hash"],
                    "status": "failed",
                    "failureReason": str(ex)
                }
                self.create_one(failed_transaction_payload)
                # emit("burn", {'assetId': data["assetId"], 'hash': data['hash'], "status": "failed"}, room=data['sid'], namespace="/notification")
                return {
                        "error": f"Something went wrong with the transaction. Transaction hash is {data['hash']}"
                    }, 503
            except Exception:
                self.logger.error(f"Failure in process_burn_transaction method for {data['assetId']} and hash {data['hash']}, Exception : {traceback.format_exc()}")
                return {
                        "error": f"Something went wrong with the transaction. Transaction hash is {data['hash']}"
                    }, 503

    def unpin_pinata_image(self, image_url):
        """ unpit pinata after nft burn """
        hash = image_url.split("/ipfs/")[1]
        url = f"https://api.pinata.cloud/pinning/unpin/{hash}"
        pinataApiKey = "3696ba7be24b33f0c237"
        pinataSecretApiKey='b9bf1ca720dc74402c979fca0a8f7e2b8f8e4f747170a7d01dcc1eb6e8e4034c'
        headers = {
            "pinata_api_key": pinataApiKey,
            "pinata_secret_api_key": pinataSecretApiKey,
            "Content-Type": "application/json"
        }
        resp = requests.delete(url, headers=headers, verify=False)
        if resp.status_code != 200:
            print(f"Image with hash {hash} failed to unpin, error {resp.text}")
            self.logger.error(f"Image with hash {hash} failed to unpin, error {resp.text}")
            return resp
        else:
            print(f"Image with hash {hash} unpinned successfully")
            self.logger.info(f"Image with hash {hash} unpinned successfully")
            return {"message": f"Image with hash {hash} unpinned successfully"}, 200
        