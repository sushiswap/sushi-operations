import sys
import os
import json
import time
import math
import argparse
from web3 import Web3, HTTPProvider
from web3.logs import DISCARD
from eth_abi import encode

from utils.config import RPC_URL, CHAIN_MAP, WETH_SERVER_ADDRESSES, BASE_ADDRESS, MIN_USD_VAL
from utils.graph_data import fetch_lp_tokens
from utils.token_list import fetch_whitelisted_tokens

# Retrieve job-defined env vars
TASK_INDEX = os.getenv("CLOUD_RUN_TASK_INDEX", 0)
TASK_ATTEMPT = os.getenv("CLOUD_RUN_TASK_ATTEMPT", 0)
IGNORE_GAS = False

# Retrieve user-defined env vars
OPS_ADDRESS = os.environ["OPS_ADDRESS"]
OPS_PK = os.environ["OPS_PK"]

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

    print("Fetching LP token balances...")
    lp_tokens_data = fetch_lp_tokens(
        WETH_SERVER_ADDRESSES[chain], chain)
    print(f"Fetched {len(lp_tokens_data)} LP tokens to process...")

    # print("Fetching token list for chain {chain}...")
    # whitelisted_tokens = fetch_whitelisted_tokens(chain)
    # filtered_lp_tokens_data = [
    #    lp_token for lp_token in lp_tokens_data if lp_token['pair']['token0']['id'] in whitelisted_tokens and lp_token['pair']#['token1']['id'] in whitelisted_tokens
    # ]

    if args.burn:
        print("Burning LP tokens...")
        burn_lp_tokens(w3, lp_tokens_data)
    elif args.full:
        print("Unwinding LP tokens...")
        full_breakdown(w3, chain, lp_tokens_data)


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

        if usd_value < MIN_USD_VAL[chain]:
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
                (token0_amount - (token0_amount * 0.001)) * pow(10, int(lp_token['pair']['token0']['decimals'])))
            unwind_data['minOut_highSlippage'] = int(
                (token0_amount - (token0_amount * 0.01)) * pow(10, int(lp_token['pair']['token0']['decimals'])))

        else:
            print(f"NOT A BASE TOKEN PAIR: {lp_token['pair']['name']}")
            continue

        try:
            maker_contract.functions.unwindPairs(
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
                maker_contract.functions.unwindPairs(
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
                    maker_contract.functions.burnPairs(
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
                    burns_amounts.append(int(unwind_data['amount']))
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

    if chain is not CHAIN_MAP['polygon']:
        last_block = w3.eth.get_block('latest')
        next_gas_price = math.ceil(last_block.get('baseFeePerGas') * 1.125)
    else:
        next_gas_price = w3.eth.generate_gas_price()

    print(f"Next gas price: {next_gas_price}")

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
        print(f"Executing unwind chunk {i}")

        tx_data = maker_contract.functions.unwindPairs(
            tokenA_chunks[i],
            tokenB_chunks[i],
            unwinds_amounts_chunks[i],
            unwinds_minimumOuts_chunks[i],
        ).build_transaction({
            "chainId": CHAIN_MAP[chain],
            "from": OPS_ADDRESS,
            "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
            "maxFeePerGas": next_gas_price,
            "gas": gas_estimate
        })

        tx = w3.eth.account.sign_transaction(
            tx_data, private_key=OPS_PK)
        tx_hash = w3.eth.send_raw_transaction(tx.rawTransaction)

        try:
            tx_receipt = w3.eth.wait_for_transaction_receipt(
                tx_hash, timeoout=600)
        except:
            print(
                f"Transaction taking longer than expected, waiting 3 minutes: {tx_hash.hex()}"
            )
            time.sleep(180)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"Unwind chunk {i} executed successfully in tx: {tx_hash.hex()}")

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
        print(f"Executing burn chunk {i}")

        tx_data = maker_contract.functions.burnPairs(
            burns_lpToken_chunks[i],
            burns_amounts_chunks[i],
            burns_minimumOuts0_chunks[i],
            burns_minimumOuts1_chunks[i],
        ).build_transaction({
            "chainId": CHAIN_MAP[chain],
            "from": OPS_ADDRESS,
            "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
            "maxFeePerGas": next_gas_price,
            "gas": gas_estimate
        })
        tx = w3.eth.account.sign_transaction(
            tx_data, private_key=OPS_PK)
        tx_hash = w3.eth.send_raw_transaction(tx.rawTransaction)

        try:
            tx_receipt = w3.eth.wait_for_transaction_receipt(
                tx_hash, timeout=600)
        except:
            print(
                f"Transaction taking longer than expected, waiting 3 minutes: {tx_hash.hex()}"
            )
            time.sleep(180)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"Burn chunk {i} executed successfully in tx: {tx_hash.hex()}")

    print(f"Completed Task #{TASK_INDEX}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--burn", required=False,
                        action="store_true")
    parser.add_argument("-f", "--full", required=False,
                        action="store_true")
    parser.add_argument("--chain", required=True, type=str)

    args = parser.parse_args()

    main(args.chain, args)
