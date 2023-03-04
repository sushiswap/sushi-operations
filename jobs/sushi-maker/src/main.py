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
# os.environ["OPS_ADDRESS"]
OPS_ADDRESS = "0x4bb4c1B0745ef7B4642fEECcd0740deC417ca0a0"
OPS_PK = os.environ["OPS_PK"]

CHAIN_MAP = {
    "mainnet": 1,
    "arbitrum": 42161,
}

RPC_URL = {
    "arbitrum": ARBITRUM_RPC_URL,
}

WETH_SERVER_ADDRESSES = {
    "arbitrum": "0xa19b3b22f29E23e4c04678C94CFC3e8f202137d8",
}

WETH_ADDRESS = {
    "arbitrum": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
}

MIN_USD_VA = {
    "arbitrum": 10
}

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "abis/WethMaker.json")) as f:
    WETH_MAKER_ABI = json.load(f)


def main(chain, args):
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

    if args.burn:
        print("Burning LP tokens...")
        burn_lp_tokens(w3, lp_tokens_data)
    elif args.unwind:
        print("Unwinding LP tokens...")
        unwind_lp_tokens(w3, chain, lp_tokens_data)

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
        print(lp_token['liquidityTokenBalance'])
        print("\n")


def unwind_lp_tokens(w3, chain, lp_tokens_data):
    maker_contract = w3.eth.contract(
        w3.toChecksumAddress(WETH_SERVER_ADDRESSES[chain]),
        abi=WETH_MAKER_ABI
    )

    tokensA = []
    tokensB = []
    amounts = []
    minimumOuts = []

    for lp_token in lp_tokens_data:
        if lp_token['pair']['trackedReserveETH'] == '0':
            print(f"Bunk pair: {lp_token['pair']['name']}")
            continue

        ratio = float(lp_token['liquidityTokenBalance']) / \
            float(lp_token['pair']['totalSupply'])
        usd_value = float(lp_token['pair']['reserveUSD']) * ratio
        token0_amount = float(lp_token['pair']['reserve0']) * ratio
        token1_amount = float(lp_token['pair']['reserve1']) * ratio

        if usd_value < MIN_USD_VA[chain]:
            break

        print(f"Unwinding ${usd_value} worth of {lp_token['pair']['name']}")
        # print(lp_token['pair']['id'])

        unwind_data = {
            "tokenA": "",
            "tokenB": "",
            "amount": "",
            "minOut_lowSlippage": "",
            "minOut_highSlippage": "",
        }

        # Remove liquidity, and sell tokensB[i] for tokensA[i]
        if lp_token['pair']['token1']['id'] == WETH_ADDRESS[chain]:
            '''print(f"TokenA: {lp_token['pair']['token1']['id']}")
            print(f"TokenB: {lp_token['pair']['token0']['id']}")

            print(
                f"TokenB: {token0_amount} {lp_token['pair']['token0']['symbol']}")
            print(
                f"LP Amount: {w3.toWei(lp_token['liquidityTokenBalance'], 'ether')}")
            print(
                f"TokenA(0.1%): {w3.toWei(token1_amount - (token1_amount * 0.001), 'ether')} {lp_token['pair']['token1']['symbol']}")
            print(
                f"TokenA(10%): {w3.toWei(token1_amount - (token1_amount * 0.1), 'ether')} {lp_token['pair']['token1']['symbol']}")
            '''
            unwind_data['tokenA'] = lp_token['pair']['token1']['id']
            unwind_data['tokenB'] = lp_token['pair']['token0']['id']
            unwind_data['amount'] = w3.toWei(
                lp_token['liquidityTokenBalance'], 'ether')
            unwind_data['minOut_lowSlippage'] = w3.toWei(
                token1_amount - (token1_amount * 0.001), 'ether')
            unwind_data['minOut_highSlippage'] = w3.toWei(
                token1_amount - (token1_amount * 0.1), 'ether')

        elif lp_token['pair']['token0']['id'] == WETH_ADDRESS[chain]:
            '''print(f"TokenA: {lp_token['pair']['token0']['id']}")
            print(f"TokenB: {lp_token['pair']['token1']['id']}")

            print(
                f"TokenB: {token1_amount} {lp_token['pair']['token1']['symbol']}")
            print(
                f"LP Amount: {w3.toWei(lp_token['liquidityTokenBalance'], 'ether')}")
            print(
                f"TokenA(0.1%): {w3.toWei(token0_amount - (token0_amount * 0.001), 'ether')} {lp_token['pair']['token0']['symbol']}")
            print(
                f"TokenA(10%): {w3.toWei(token0_amount - (token0_amount * 0.1), 'ether')} {lp_token['pair']['token0']['symbol']}")

            '''

            unwind_data['tokenA'] = lp_token['pair']['token0']['id']
            unwind_data['tokenB'] = lp_token['pair']['token1']['id']
            unwind_data['amount'] = w3.toWei(
                lp_token['liquidityTokenBalance'], 'ether')
            unwind_data['minOut_lowSlippage'] = w3.toWei(
                token0_amount - (token0_amount * 0.001), 'ether')
            unwind_data['minOut_highSlippage'] = w3.toWei(
                token0_amount - (token0_amount * 0.1), 'ether')

        else:
            print(f"NOT A WETH PAIR: {lp_token['pair']['name']}")
            continue
            '''print(f"TokenA: {lp_token['pair']['token0']['id']}")
            print(f"TokenB: {lp_token['pair']['token1']['id']}")

            print(
                f"TokenA: {token0_amount} {lp_token['pair']['token0']['symbol']}")
            print(
                f"LP Amount: {w3.toWei(lp_token['liquidityTokenBalance'], 'ether')}")
            print(
                f"TokenB(0.1%): {w3.toWei(token1_amount - (token1_amount * 0.001), 'ether')} {lp_token['pair']['token1']['symbol']}")
            print(
                f"TokenB(10%): {w3.toWei(token1_amount - (token1_amount * 0.1), 'ether')} {lp_token['pair']['token1']['symbol']}")'''

        # estimate gas, to check which slippage to use
        last_block = w3.eth.get_block('latest')
        next_gas_price = math.ceil(last_block.get('baseFeePerGas') * 1.125)

        try:
            estimate_result = maker_contract.functions.unwindPairs(
                [w3.toChecksumAddress(unwind_data['tokenA'])],
                [w3.toChecksumAddress(unwind_data['tokenB'])],
                [int(unwind_data['amount'])],
                [int(unwind_data['minOut_lowSlippage'])],
            ).estimate_gas({
                "chainId": CHAIN_MAP[chain],
                "from": OPS_ADDRESS,
                "nonce": w3.eth.get_transaction_count(OPS_ADDRESS)
            })

            tokensA.append(unwind_data['tokenA'])
            tokensB.append(unwind_data['tokenB'])
            amounts.append(unwind_data['amount'])
            minimumOuts.append(unwind_data['minOut_lowSlippage'])

        except Exception as err:
            # try again with max slippage
            try:
                estimate_result = maker_contract.functions.unwindPairs(
                    [w3.toChecksumAddress(unwind_data['tokenA'])],
                    [w3.toChecksumAddress(unwind_data['tokenB'])],
                    [int(unwind_data['amount'])],
                    [int(unwind_data['minOut_highSlippage'])],
                ).estimate_gas({
                    "chainId": CHAIN_MAP[chain],
                    "from": OPS_ADDRESS,
                    "nonce": w3.eth.get_transaction_count(OPS_ADDRESS)
                })

                tokensA.append(unwind_data['tokenA'])
                tokensB.append(unwind_data['tokenB'])
                amounts.append(unwind_data['amount'])
                minimumOuts.append(unwind_data['minOut_highSlippage'])
            except Exception as err:
                print(
                    f"Likely Bunk Token, Should Burn: {lp_token['pair']['name']}")
                continue

    print("Length of unwind data")
    print(f"Number of pairs: {len(tokensA)}")

    tokenA_chunks = [tokensA[x:x+10] for x in range(0, len(tokensA), 10)]
    tokenB_chunks = [tokensB[x:x+10] for x in range(0, len(tokensB), 10)]
    amounts_chunks = [amounts[x:x+10] for x in range(0, len(amounts), 10)]
    minimumOuts_chunks = [minimumOuts[x:x+10]
                          for x in range(0, len(minimumOuts), 10)]

    for i in range(len(tokenA_chunks)):
        # call unwinds here with chunk
        print(tokenA_chunks[i])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--burn", required=False,
                        action="store_true")
    parser.add_argument("-u", "--unwind", required=False,
                        action="store_true")
    parser.add_argument("--chain", required=True, type=str)

    args = parser.parse_args()

    main(args.chain, args)
