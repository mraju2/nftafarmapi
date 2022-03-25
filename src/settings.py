""" Application Settings """
import os, json, ast
# Flask settings
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', True)
# API protected
API_UNPROTECTED = os.environ.get('API_UNPROTECTED', "TRUE")
# Token Expiration Time
TOKEN_EXPIRATION_TIME = os.environ.get('TOKEN_EXPIRATION_TIME', 1)
# Database settings
DB_PORT = os.environ.get('DB_PORT', 27017)
DB_HOST = os.environ.get('DB_HOST','nft-farm') #'localhost' 'my-mongodb'
DB_USER = os.environ.get('DB_USER', 'metalauncher') # 'root'
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'tsip292015')
USE_MONGO = os.environ.get('USE_MONGO', 'True')
ERC721_ADDRESS = os.environ.get('ERC721_ADDRESS', '0x4b8D4D4B3ea6927eB438002f8CC4713315118aAf')
BLOCK_CHAIN = os.environ.get('BLOCK_CHAIN',"BNB")
if BLOCK_CHAIN == "BNB":
    TESTNET_URL = os.environ.get('TESTNET_URL', 'https://bsc-dataseed.binance.org/') #https://bsc-dataseed.binance.org/
else:
    TESTNET_URL = os.environ.get('TESTNET_URL', 'https://http-mainnet.hecochain.com') #https://http-testnet.hecochain.com:
BLOCK_DB_NAME=os.environ.get('BLOCK_DB_NAME','nft-alley')
