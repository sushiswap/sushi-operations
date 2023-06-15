import sys
import os
import time
import json
import math
import argparse
from web3 import Web3, HTTPProvider
from eth_abi import encode
from utils.config import RPC_URLS, DISPERSE_ADDRESS, CHAIN_MAP


OPS_ADDRESS = os.environ["OPS_ADDRESS"]
OPS_PRIVATE_KEY = os.environ["OPS_PRIVATE_KEY"]

with open("abis/ERC20.json") as f:
    ERC20_ABI = json.load(f)

with open("abis/Disperse.json") as f:
    DISPERSE_ABI = json.load(f)

def main(network, token_address, amount):
    print(f"Airdropping {token_address} on {network}...")

    w3 = Web3(Web3.HTTPProvider(RPC_URLS[network]))

    if not w3.isConnected:
        print(f"Could not connect to {network} RPC")
        return RuntimeError

    if network in ["mainnet", "arbitrum"]:
        last_block = w3.eth.get_block("latest")
        next_gas_price = math.ceil(last_block.get("baseFeePerGas") * 1.125)
    else:
        next_gas_price = w3.eth.gas_price 

    disperse_contract = w3.eth.contract(
        w3.toChecksumAddress(DISPERSE_ADDRESS[network]), abi=DISPERSE_ABI
    )
    erc20_contract = w3.eth.contract(
        w3.toChecksumAddress(token_address), abi=ERC20_ABI
    )

    # get token's decimals
    token_decimals = erc20_contract.functions.decimals().call()

    # loop through txt file and scrape wallet addresses
    with open("./data/wallet-list.txt", "r") as f:
        wallet_list = f.readlines()
        wallet_list = [w3.toChecksumAddress(wallet.strip()) for wallet in wallet_list]


    # approve disperse contract
    gas_estimate = erc20_contract.functions.approve(DISPERSE_ADDRESS[network], (int(amount) * len(wallet_list)) * (10 ** token_decimals)).estimateGas(
      {
        "chainId": CHAIN_MAP[network],
        "from": OPS_ADDRESS,
        "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
      }
    )
    tx = erc20_contract.functions.approve(DISPERSE_ADDRESS[network], (int(amount) * len(wallet_list)) * (10 ** token_decimals)).buildTransaction(
        {
            "chainId": CHAIN_MAP[network],
            "from": OPS_ADDRESS,
            "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
            "gasPrice": next_gas_price,
            "gas": gas_estimate,
        }
    )
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=OPS_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    try:
      tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=1200)
    except:
      print(
        f"Transaction taking longer than expected, waiting 3 minutes: {tx_hash.hex()}"
      )
      time.sleep(180)
      tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Approval Transaction successful: {tx_receipt.transactionHash.hex()}")

    # create list of amounts to airdrop
    amounts = [(int(amount)) * (10 ** token_decimals)] * len(wallet_list)

    # disperse call
    gas_estimate = disperse_contract.functions.disperseToken(w3.toChecksumAddress(token_address), wallet_list, amounts).estimateGas(
      {
        "chainId": CHAIN_MAP[network],
        "from": OPS_ADDRESS,
        "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
      }
    )

    tx = disperse_contract.functions.disperseToken(w3.toChecksumAddress(token_address), wallet_list, amounts).buildTransaction(
        {
            "chainId": CHAIN_MAP[network],
            "from": OPS_ADDRESS,
            "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
            "gasPrice": next_gas_price,
            "gas": gas_estimate,
        }
    )
    
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=OPS_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    try:
      tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=1200)
    except:
      print(
        f"Transaction taking longer than expected, waiting 3 minutes: {tx_hash.hex()}"
      )
      time.sleep(180)
      tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Transaction successful: {tx_receipt.transactionHash.hex()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", help="network name")
    parser.add_argument("--token", help="token address")
    parser.add_argument("--amount", help="amount to airdrop")

    args = parser.parse_args()

    main(args.network, args.token, args.amount)