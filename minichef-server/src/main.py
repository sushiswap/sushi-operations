import sys
import os
import json
import time
import math
from web3 import Web3, HTTPProvider
from web3.logs import DISCARD
from eth_abi import encode

from utils.gas import gas_price_arbitrum, get_arbitrum_retryable_submission_fee

# Retrieve job-defined env vars
TASK_INDEX = os.getenv("CLOUD_RUN_TASK_INDEX", 0)
TASK_ATTEMPT = os.getenv("CLOUD_RUN_TASK_ATTEMPT", 0)
# Retrieve user-defined env vars
MAINNET_RPC_URL = os.environ["MAINNET_RPC_URL"]
OPS_ADDRESS = os.environ["OPS_ADDRESS"]
OPS_PK = os.environ["OPS_PK"]

OLD_SERVER_ADDRESSES = {
    "polygon": "0x3d0B3b816DC1e0825808F27510eF7Aa5E3136D75",
    "celo": "0x6eB21D6d8E272Aa07B49D12ABc51B839e1dE0216",
    "gnosis": "0xBbD10280DD13de418f666648D2488e4059F56d81",
}

NO_DATA_SERVER_ADDRESSES = {
    "bttc": "0xc4D1dE66c678580A84008441c44AF8276cd2E0F9",
    "bsc": "0x993cb187344747374750d8Bc1dBB50845400A638",
    "kava": "0xf0ACd9fc9c752e6ee46aE166aeD27faa7a159F21"
}

DATA_SERVER_ADDRESS = {
    "arbitrum": "0xE0A6e30B676ef084d7Ed6495dE55e59a7fd2bCbe",
    "arbitrum-nova": "0xFFd482298a65D0E16198ccdCEFE2360c7b47990B",
    "boba": "0xd8108F6546222ebf42020e2f213AC8785AF99488",
    "metis": "0xBd91B3BeF78787f3b4bc5251E830BBE7dF93168E"
}

MULTICALL_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "abis/OldServer.json")) as f:
    OLD_SERVER_ABI = json.load(f)
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "abis/BaseServer.json")) as f:
    DATA_SERVER_ABI = json.load(f)
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "abis/Multicall3.json")) as f:
    MULTICALL_ABI = json.load(f)


def main():
    print("Running MiniChef Servers Job")
    print(f"Starting Task #{TASK_INDEX}, Atempt #{TASK_ATTEMPT}...")

    w3 = Web3(Web3.HTTPProvider(MAINNET_RPC_URL))
    if not w3.isConnected:
        print("Could not connect to mainnet RPC")
        return RuntimeError

    last_block = w3.eth.get_block('latest')
    next_gas_price = math.ceil(last_block.get('baseFeePerGas') * 1.125)

    if (next_gas_price > 40e9):
        print(f"Gas price is too high: {next_gas_price}")
        return RuntimeError

    calls_to_make = []
    multicall_contract = w3.eth.contract(
        w3.toChecksumAddress(MULTICALL_ADDRESS), abi=MULTICALL_ABI)

    print(f"Current block is: {w3.eth.blockNumber}")

    print("Serving Old MiniChef Servers...")
    calls_to_make.extend(bridge_old_servers(w3))

    print("Serving No Data MiniChef Servers...")
    calls_to_make.extend(bridge_nodata_servers(w3))

    print("Serving Data MiniChef Servers...")
    calls_to_make.extend(bridge_data_servers(w3))

    # add up eth to send for each val in calls_to_make
    total_eth_to_send = sum(calls['value'] for calls in calls_to_make)

    tx_data = multicall_contract.functions.aggregate3Value(calls_to_make).build_transaction({
        "chainId": 1,
        "from": OPS_ADDRESS,
        "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
        "maxFeePerGas": next_gas_price,
        "gas": 2000000,
        "value": total_eth_to_send
    })
    tx = w3.eth.account.sign_transaction(tx_data, private_key=OPS_PK)
    tx_hash = w3.eth.send_raw_transaction(tx.rawTransaction)

    try:
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
    except:
        print(
            f"Transaction taking longer than expected, waiting 3 minutes: {tx_hash.hex()}")
        time.sleep(180)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f'Servers served in tx: {tx_hash.hex()}')

    print(f"Completed Task #{TASK_INDEX}.")


def bridge_old_servers(w3):
    calls_to_make = []
    for server_key in OLD_SERVER_ADDRESSES:
        print(f"Serving {server_key} Server...")
        server_contract = w3.eth.contract(w3.toChecksumAddress(
            OLD_SERVER_ADDRESSES[server_key]), abi=OLD_SERVER_ABI)
        calls_to_make.append(
            {
                "target": server_contract.address,
                "allowFailure": True,
                "value": 0,
                "callData": server_contract.encodeABI(fn_name="harvestAndBridge")
            }
        )
    return calls_to_make


def bridge_eoa_servers(w3):
    return


def bridge_nodata_servers(w3):
    calls_to_make = []
    for server_key in NO_DATA_SERVER_ADDRESSES:
        print(f"Serving {server_key} Server...")
        server_contract = w3.eth.contract(w3.toChecksumAddress(
            NO_DATA_SERVER_ADDRESSES[server_key]), abi=DATA_SERVER_ABI)
        calls_to_make.append(
            {
                "target": server_contract.address,
                "allowFailure": True,
                "value": 0,
                "callData": server_contract.encodeABI(fn_name="harvestAndBridge", args=['0x'])
            }
        )
    return calls_to_make


def bridge_data_servers(w3):
    calls_to_make = []
    for server_key in DATA_SERVER_ADDRESS:
        match server_key:
            case "arbitrum":
                calls_to_make.append(bridge_arbitrum(w3, False))
            case "arbitrum-nova":
                calls_to_make.append(bridge_arbitrum(w3, True))
            case "boba":
                calls_to_make.append(bridge_op_style(w3, server_key))
            case "metis":
                calls_to_make.append(bridge_op_style(w3, server_key))
            case _:
                continue

    return calls_to_make


def bridge_op_style(w3, key):
    if key == "boba":
        boba_sushi_token = "0x5fFccc55C0d2fd6D3AC32C26C020B3267e933F1b"
        l2_gas = 1300000
        bridge_data = encode(['address', 'uint32', 'bytes'], [
            boba_sushi_token, l2_gas, Web3.toBytes(text='')])
    elif key == "metis":
        l2_gas = 200000
        bridge_data = encode(['uint32', 'bytes'], [
            l2_gas, Web3.toBytes(text='')])
    print(f"Serving {key} Server...")
    server_contract = w3.eth.contract(w3.toChecksumAddress(
        DATA_SERVER_ADDRESS[key]), abi=DATA_SERVER_ABI)

    return {
        "target": server_contract.address,
        "allowFailure": True,
        "value": 0,
        "callData": server_contract.encodeABI(fn_name="harvestAndBridge", args=[Web3.toHex(bridge_data)])
    }


def bridge_arbitrum(w3, isNova):
    key = "arbitrum-nova" if isNova else "arbitrum"
    print(f"Serving {key} Server...")
    server_contract = w3.eth.contract(w3.toChecksumAddress(
        DATA_SERVER_ADDRESS[key]), abi=DATA_SERVER_ABI)
    l2_transfer_gas_limit = 96190
    gas_price_bid = gas_price_arbitrum(isNova)
    max_submission_fee = get_arbitrum_retryable_submission_fee(isNova)
    eth_to_send = (l2_transfer_gas_limit * gas_price_bid) / \
        1e16 * 0.6 + (l2_transfer_gas_limit * gas_price_bid) / 1e16
    extra_data = encode(['uint256', 'bytes'], [
                        max_submission_fee, Web3.toBytes(text='')])[:-32]
    bridge_data = encode(['address', 'uint256', 'uint256', 'bytes'], [
        OPS_ADDRESS, l2_transfer_gas_limit, gas_price_bid, extra_data])

    return {
        "target": server_contract.address,
        "allowFailure": True,
        "value": Web3.toWei(eth_to_send, 'ether'),
        "callData": server_contract.encodeABI(fn_name="bridge", args=[Web3.toHex(bridge_data)])
    }


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        message = f"Task #{TASK_INDEX}, " \
            + f"Attempt #{TASK_ATTEMPT} failed: {str(err)}"
        print(json.dumps({"message": message, "severity": "ERROR"}))
        sys.exit(1)  # Retry Job Task by exiting the process
