import os
import json

import requests
from web3 import Web3, HTTPProvider


MAINNET_RPC_URL = os.environ["MAINNET_RPC_URL"]
ARBITRUM_RPC_URL = os.environ["ARBITRUM_RPC_URL"]
ARBITRUM_NOVA_RPC_URL = "https://nova.arbitrum.io/rpc"
BOBA_RPC_URL = "https://mainnet.boba.network"

ARBITRUM_INBOX = "0x4Dbd4fc535Ac27206064B68FfCf827b0A60BAB3f"
ARBITRUM_NOVA_INBOX_ADDRESS = "0xc4448b71118c9071Bcb9734A0EAc55D18A153949"


def gas_price_mainnet():
    w3 = Web3(Web3.HTTPProvider(MAINNET_RPC_URL))
    return w3.eth.gasPrice


def gas_price_arbitrum(isNova):
    if isNova:
        w3 = Web3(Web3.HTTPProvider(ARBITRUM_NOVA_RPC_URL))
    else:
        w3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC_URL))

    return w3.eth.gasPrice


def gas_price_boba():
    w3 = Web3(Web3.HTTPProvider(BOBA_RPC_URL))
    return w3.eth.gasPrice


def get_arbitrum_retryable_submission_fee(isNova):
    w3 = Web3(Web3.HTTPProvider(MAINNET_RPC_URL))

    with open(os.path.join(os.path.dirname(os.path.realpath('__main__')), "abis/Inbox.json")) as f:
        inbox_abi = json.load(f)

    inbox_address = ARBITRUM_NOVA_INBOX_ADDRESS if isNova else ARBITRUM_INBOX
    inbox_contract = w3.eth.contract(
        w3.toChecksumAddress(inbox_address), abi=inbox_abi)
    # passing 0 uses last block base fee for the calculation
    return inbox_contract.functions.calculateRetryableSubmissionFee(800, 0).call()
