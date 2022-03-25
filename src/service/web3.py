""" Web3 Service"""

import json
from eth_typing.evm import ChecksumAddress
from web3 import Web3
import web3
from web3.middleware import geth_poa_middleware
from service.service_base import ServiceBase
from eth_account.messages import encode_defunct, defunct_hash_message
from datetime import datetime, timezone
from settings import TESTNET_URL, ERC721_ADDRESS

class Web3Alley(ServiceBase):
    """ Web3 Service """

    def __init__(self):
        """ web3 connection"""
        # HTTPProvider:
        self.w3 = Web3(Web3.HTTPProvider(TESTNET_URL))

    def get_transaction_receipt(self, txHash):
        """ web3 get transaction receipt """
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(txHash, timeout=600, poll_latency=0.1)
            return json.loads(Web3.toJSON(receipt)), 200
        except web3.exceptions.TimeExhausted:
            return {"error": "tranction timed out"}, 408
        except Exception as ex:
            return {
                "error": "something wrong with transaction hash",
                "message": ex
            }, 404

    def get_block_time(self, blockNumber):
        try:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            block_num = self.w3.eth.getBlock(blockNumber).timestamp
            return str(block_num)
        except Exception:
            str(datetime.now(timezone.utc).timestamp())


    def decode_sign(self, address, input, sign):
        """ decode signature """
        validAddress = self.w3.toChecksumAddress(address)
        base_msg = self.w3.soliditySha3(["address", "uint256"], [validAddress, self.w3.toWei(input, "ether")])
        message = encode_defunct(base_msg)
        return self.w3.eth.account.recover_message(message, signature=sign)

    
    def read_sign(self, textMsg, sign):
        """ read signature """
        message = defunct_hash_message(text=textMsg)
        return self.w3.eth.account.recoverHash(message, signature=sign)

    
    def convert_hex_to_number_string(self, hex):
        """ convert hex to number """
        return str(self.w3.toInt(hexstr=hex))

