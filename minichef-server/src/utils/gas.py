import os

import requests
from web3 import Web3, HTTPProvider


MAINNET_RPC_URL = os.environ["MAINNET_RPC_URL"]
ARBITRUM_RPC_URL = os.environ["ARBITRUM_RPC_URL"]

def gas_price_mainnet():
  w3 = Web3(Web3.HTTPProvider(MAINNET_RPC_URL))
  return w3.eth.gasPrice


def gas_price_arbitrum():
  w3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC_URL))
  return w3.eth.gasPrice