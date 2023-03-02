import sys
import os
import json
import time
import math
import argparse
from web3 import Web3, HTTPProvider
from web3.logs import DISCARD
from eth_abi import encode

from utils.graph_data import fetch_lp_tokens
from utils.token_list import fetch_whitelisted_tokens

# Retrieve job-defined env vars
TASK_INDEX = os.getenv("CLOUD_RUN_TASK_INDEX", 0)
TASK_ATTEMPT = os.getenv("CLOUD_RUN_TASK_ATTEMPT", 0)
RUN_PRIORITY = False
RUN_NON_PRIORITY = False
IGNORE_GAS = False

# Retrieve user-defined env vars
MAINNET_RPC_URL = os.environ["MAINNET_RPC_URL"]
ARBITRUM_RPC_URL = os.environ["ARBITRUM_RPC_URL"]
OPS_ADDRESS = os.environ["OPS_ADDRESS"]
OPS_PK = os.environ["OPS_PK"]


RPC_URL = {
    "arbitrum": ARBITRUM_RPC_URL,
}

WETH_SERVER_ADDRESSES = {
    "arbitrum": "0xa19b3b22f29E23e4c04678C94CFC3e8f202137d8",
}

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "abis/WethMaker.json")) as f:
    WETH_MAKER_ABI = json.load(f)


def main(chain):
    print("Running WethMaker Job")
    print(f"Starting Task {TASK_INDEX} Attempt {TASK_ATTEMPT}...")

    w3 = Web3(Web3.HTTPProvider(RPC_URL[chain]))
    if not w3.isConnected():
        print(f"Failed to connect to {chain}")
        return RuntimeError

    last_block = w3.eth.get_block("latest")
    # next_gas_price
    # gas price checks if should run script goes here
    print(f"Current block: {last_block['number']}")

    print("Fetching LP token balances...")
    lp_tokens_data = fetch_lp_tokens(
        WETH_SERVER_ADDRESSES[chain], chain)
    print(f"Fetched {len(lp_tokens_data)} LP tokens to burn...")

    print("Fetching token list for chain {chain}...")
    whitelisted_tokens = fetch_whitelisted_tokens(chain)
    filtered_lp_tokens_data = [
        lp_token for lp_token in lp_tokens_data if lp_token['pair']['token0']['id'] in whitelisted_tokens and lp_token['pair']['token1']['id'] in whitelisted_tokens
    ]

    burn_lp_tokens(w3, filtered_lp_tokens_data)

    # fetch all lp tokens maker is holding

    # process and structure data to make burn calls

    # burn all lp tokens into individual tokens

    # sell all tokens for weth, watch for no bridge set and large slippage that should revert tx

    # unwind_lp_tokens(w3)


def burn_lp_tokens(w3, lp_tokens_data):
    for lp_token in lp_tokens_data:
        if lp_token['pair']['trackedReserveETH'] == '0':
            print(f"Bunk pair: {lp_token['pair']['name']}")
            continue
        usd_value = float(lp_token['pair']['reserveUSD']) * (
            float(lp_token['liquidityTokenBalance']) / float(lp_token['pair']['totalSupply']))
        print(f"Burning ${usd_value} worth of {lp_token['pair']['name']}")
        print(lp_token['pair']['id'])


def unwind_lp_tokens(w3):

    return


if __name__ == "__main__":
    main("arbitrum")
