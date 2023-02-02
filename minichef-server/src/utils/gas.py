import os
import json

import requests
from web3 import Web3, HTTPProvider


MAINNET_RPC_URL = os.environ["MAINNET_RPC_URL"]
ARBITRUM_RPC_URL = os.environ["ARBITRUM_RPC_URL"]

ARBITRUM_INBOX_ADDRESS = "0xc4448b71118c9071Bcb9734A0EAc55D18A153949"


def gas_price_mainnet():
    w3 = Web3(Web3.HTTPProvider(MAINNET_RPC_URL))
    return w3.eth.gasPrice


def gas_price_arbitrum():
    w3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC_URL))
    return w3.eth.gasPrice


def get_arbitrum_retryable_submission_fee():
    w3 = Web3(Web3.HTTPProvider(MAINNET_RPC_URL))

    with open(os.path.join(os.path.dirname(os.path.realpath('__main__')), "abis/Inbox.json")) as f:
        inbox_abi = json.load(f)

    inbox_contract = w3.eth.contract(
        w3.toChecksumAddress(ARBITRUM_INBOX_ADDRESS), abi=inbox_abi)
    # passing 0 uses last block base fee for the calculation
    return inbox_contract.functions.calculateRetryableSubmissionFee(740, gas_price_mainnet()).call()
