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
    "mainnet": MAINNET_RPC_URL,
    "arbitrum": ARBITRUM_RPC_URL,
}

WETH_SERVER_ADDRESSES = {
    "mainnet": "0x5ad6211CD3fdE39A9cECB5df6f380b8263d1e277",
    "arbitrum": "0xa19b3b22f29E23e4c04678C94CFC3e8f202137d8",
}

BASE_ADDRESS = {
    "mainnet": [
        "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
        "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
        "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
        "0xdac17f958d2ee523a2206206994597c13d831ec7",  # USDT
        "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",  # WBTC
        "0xd533a949740bb3306d119cc777fa900ba034cd52",  # CRV
        "0x853d955acef822db058eb8505911ed77f175b99e",  # FRAX
    ],
    "arbitrum": [
        "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",  # WETH
        "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8",  # USDC
        "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",  # DAI
        "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",  # USDT
        "0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f",  # WBTC
    ],
}

MIN_USD_VA = {
    "mainnet": 100,
    "arbitrum": 100
}

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "abis/WethMaker.json")) as f:
    WETH_MAKER_ABI = json.load(f)

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "abis/Pair.json")) as f:
    PAIR_ABI = json.load(f)


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
    print(f"Fetched {len(lp_tokens_data)} LP tokens to process...")

    print("Fetching token list for chain {chain}...")
    whitelisted_tokens = fetch_whitelisted_tokens(chain)
    filtered_lp_tokens_data = [
        lp_token for lp_token in lp_tokens_data if lp_token['pair']['token0']['id'] in whitelisted_tokens and lp_token['pair']['token1']['id'] in whitelisted_tokens
    ]

    if args.burn:
        print("Burning LP tokens...")
        burn_lp_tokens(w3, lp_tokens_data)
    elif args.full:
        print("Unwinding LP tokens...")
        full_breakdown(w3, chain, lp_tokens_data)

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


def full_breakdown(w3, chain, lp_tokens_data):
    maker_contract = w3.eth.contract(
        w3.toChecksumAddress(WETH_SERVER_ADDRESSES[chain]),
        abi=WETH_MAKER_ABI
    )

    unwinds_tokensA = []
    unwinds_tokensB = []
    unwinds_amounts = []
    unwinds_minimumOuts = []

    burns_lpTokens = []
    burns_amounts = []
    burns_minimumOuts0 = []
    burns_minimumOuts1 = []

    total_usd_unwind = 0
    total_usd_burn = 0

    for lp_token in lp_tokens_data:
        # fetch up to date liquidity token balance
        pair_contract = w3.eth.contract(
            w3.toChecksumAddress(lp_token['pair']['id']),
            abi=PAIR_ABI
        )
        lp_token_balance = pair_contract.functions.balanceOf(
            w3.toChecksumAddress(WETH_SERVER_ADDRESSES[chain])).call()

        ratio = float(lp_token_balance / 1e18) / \
            float(lp_token['pair']['totalSupply'])
        usd_value = float(lp_token['pair']['reserveUSD']) * ratio
        token0_amount = float(lp_token['pair']['reserve0']) * ratio
        token1_amount = float(lp_token['pair']['reserve1']) * ratio

        if usd_value < MIN_USD_VA[chain]:
            break

        unwind_data = {
            "tokenA": "",
            "tokenB": "",
            "amount": "",
            "minOut_lowSlippage": "",
            "minOut_highSlippage": "",
        }

        # Remove liquidity, and sell tokensB[i] for tokensA[i]
        if lp_token['pair']['token1']['id'] in BASE_ADDRESS[chain]:
            unwind_data['tokenA'] = lp_token['pair']['token1']['id']
            unwind_data['tokenB'] = lp_token['pair']['token0']['id']
            unwind_data['amount'] = lp_token_balance
            unwind_data['minOut_lowSlippage'] = int(
                (token1_amount - (token1_amount * 0.005)) * pow(10, int(lp_token['pair']['token1']['decimals'])))
            unwind_data['minOut_highSlippage'] = int(
                (token1_amount - (token1_amount * 0.5)) * pow(10, int(lp_token['pair']['token1']['decimals'])))

        elif lp_token['pair']['token0']['id'] in BASE_ADDRESS[chain]:
            unwind_data['tokenA'] = lp_token['pair']['token0']['id']
            unwind_data['tokenB'] = lp_token['pair']['token1']['id']
            unwind_data['amount'] = lp_token_balance
            unwind_data['minOut_lowSlippage'] = int(
                (token0_amount - (token0_amount * 0.005)) * pow(10, int(lp_token['pair']['token0']['decimals'])))
            unwind_data['minOut_highSlippage'] = int(
                (token0_amount - (token0_amount * 0.5)) * pow(10, int(lp_token['pair']['token0']['decimals'])))

        else:
            print(f"NOT A BASE TOKEN PAIR: {lp_token['pair']['name']}")
            continue

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

            print(
                f"Unwinding(low slippage) ${usd_value} worth of {lp_token['pair']['name']}")
            total_usd_unwind += usd_value
            unwinds_tokensA.append(w3.toChecksumAddress(unwind_data['tokenA']))
            unwinds_tokensB.append(w3.toChecksumAddress(unwind_data['tokenB']))
            unwinds_amounts.append(unwind_data['amount'])
            unwinds_minimumOuts.append(unwind_data['minOut_lowSlippage'])

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

                print(
                    f"Unwinding (high slippage) ${usd_value} worth of {lp_token['pair']['name']}")
                total_usd_unwind += usd_value
                unwinds_tokensA.append(
                    w3.toChecksumAddress(unwind_data['tokenA']))
                unwinds_tokensB.append(
                    w3.toChecksumAddress(unwind_data['tokenB']))
                unwinds_amounts.append(unwind_data['amount'])
                unwinds_minimumOuts.append(unwind_data['minOut_highSlippage'])
            except Exception as err:
                try:
                    estimate_result = maker_contract.functions.burnPairs(
                        [w3.toChecksumAddress(lp_token['pair']['id'])],
                        [int(unwind_data['amount'])],
                        [0],
                        [0],
                    ).estimate_gas({
                        "chainId": CHAIN_MAP[chain],
                        "from": OPS_ADDRESS,
                        "nonce": w3.eth.get_transaction_count(OPS_ADDRESS)
                    })

                    print(f"Burning {lp_token['pair']['name']}")

                    total_usd_burn += usd_value
                    burns_lpTokens.append(
                        w3.toChecksumAddress(lp_token['pair']['id']))
                    burns_amounts.append(unwind_data['amount'])
                    burns_minimumOuts0.append(0)
                    burns_minimumOuts1.append(0)

                except Exception as err:
                    print(
                        f"Likely Bunk Token, can't Unwind/Burn: {lp_token['pair']['name']}")
                    print("\n")
                    print('-- Needs possible manual actions --')
                    print(f"{lp_token['pair']['name']}")
                    print(f"LP Token: {lp_token['pair']['id']}")
                    print(f"TokenA: {unwind_data['tokenA']}")
                    print(f"TokenB: {unwind_data['tokenB']}")
                    print(f"Amount: {unwind_data['amount']}")
                    print(
                        f"TokenA Out(low): {unwind_data['minOut_lowSlippage']}")
                    print(
                        f"TokenA Out(high): {unwind_data['minOut_highSlippage']}")
                    print("\n")

                    continue

    print("Length of unwind data")
    print(f"Number of pairs: {len(unwinds_tokensA)}")
    print(f"Value of unwinds: ${total_usd_unwind}")
    print(f"Value of burns: ${total_usd_burn}")

    tokenA_chunks = [unwinds_tokensA[x:x+10]
                     for x in range(0, len(unwinds_tokensA), 10)]
    tokenB_chunks = [unwinds_tokensB[x:x+10]
                     for x in range(0, len(unwinds_tokensB), 10)]
    unwinds_amounts_chunks = [unwinds_amounts[x:x+10]
                              for x in range(0, len(unwinds_amounts), 10)]
    unwinds_minimumOuts_chunks = [unwinds_minimumOuts[x:x+10]
                                  for x in range(0, len(unwinds_minimumOuts), 10)]

    burns_lpToken_chunks = [burns_lpTokens[x:x+10]
                            for x in range(0, len(burns_lpTokens), 10)]
    burns_amounts_chunks = [burns_amounts[x:x+10]
                            for x in range(0, len(burns_amounts), 10)]
    burns_minimumOuts0_chunks = [burns_minimumOuts0[x:x+10]
                                 for x in range(0, len(burns_minimumOuts0), 10)]
    burns_minimumOuts1_chunks = [burns_minimumOuts1[x:x+10]
                                 for x in range(0, len(burns_minimumOuts1), 10)]

    print(f"Uwninding {len(unwinds_tokensA)} pairs")
    for i in range(len(tokenA_chunks)):
        # call unwinds here with chunk
        gas_estimate = maker_contract.functions.unwindPairs(
            tokenA_chunks[i],
            tokenB_chunks[i],
            unwinds_amounts_chunks[i],
            unwinds_minimumOuts_chunks[i],
        ).estimate_gas({
            "chainId": CHAIN_MAP[chain],
            "from": OPS_ADDRESS,
            "nonce": w3.eth.get_transaction_count(OPS_ADDRESS)
        })

        print(f"Full unwind gas estimate chunk {i}: {gas_estimate}")

    print(f"Burning {len(burns_lpTokens)} pairs")
    for i in range(len(burns_lpToken_chunks)):
        # call burns here with chunk
        gas_estimate = maker_contract.functions.burnPairs(
            burns_lpToken_chunks[i],
            burns_amounts_chunks[i],
            burns_minimumOuts0_chunks[i],
            burns_minimumOuts1_chunks[i],
        ).estimate_gas({
            "chainId": CHAIN_MAP[chain],
            "from": OPS_ADDRESS,
            "nonce": w3.eth.get_transaction_count(OPS_ADDRESS)
        })

        print(f"Full burn gas estimate chunk {i}: {gas_estimate}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--burn", required=False,
                        action="store_true")
    parser.add_argument("-f", "--full", required=False,
                        action="store_true")
    parser.add_argument("--chain", required=True, type=str)

    args = parser.parse_args()

    main(args.chain, args)
