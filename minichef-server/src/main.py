import sys
import os
import json
import time
from web3 import Web3, HTTPProvider
from web3.logs import DISCARD
from web3.gas_strategies.time_based import fast_gas_price_strategy
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
    "bsc": "0xC45A496BcC9ba69FFB45303f7515739C3F6FF921",
    "kava": "0x2595CbF29caCdac30c192bD2B7B4f011DeF910aD"
}

DATA_SERVER_ADDRESS = {
    "arbitrum": "0xA0347f683BF2e64b5fF54Ca9Ffc2215E7413DB76",
    "arbitrum-nova": "0x1cF5bbfEC4783651a90ddF148c94D622Ac05e4a0",
    "boba": "0x8207B70432211EeeB0445E666F3201C42d38F7f5",
    "metis": "0xAa9A2D4a7f4BB7a037911d52a05eF6600fC0cB81"
}


with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "abis/OldServer.json")) as f:
    OLD_SERVER_ABI = json.load(f)
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "abis/BaseServer.json")) as f:
    DATA_SERVER_ABI = json.load(f)


def main():
    print("Running MiniChef Servers Job")
    print(f"Starting Task #{TASK_INDEX}, Atempt #{TASK_ATTEMPT}...")

    w3 = Web3(Web3.HTTPProvider(MAINNET_RPC_URL))
    w3.eth.set_gas_price_strategy(fast_gas_price_strategy)
    if not w3.isConnected:
        print("Could not connect to mainnet RPC")
        return RuntimeError

    # if (w3.eth.gasPrice > 30e9):
    #    print(f"Gas price is too high: {w3.eth.gasPrice}")
    #    return RuntimeError

    print(f"Current block is: {w3.eth.blockNumber}")

    print("Serving Old MiniChef Servers...")
    # bridge_old_servers(w3)

    print("Serving No Data MiniChef Servers...")
    # bridge_nodata_servers(w3)

    print("Serving Data MiniChef Servers...")
    bridge_data_servers(w3)

    print(f"Completed Task #{TASK_INDEX}.")


def bridge_old_servers(w3):
    for server_key in OLD_SERVER_ADDRESSES:
        print(f"Serving {server_key} Server...")
        server_contract = w3.eth.contract(w3.toChecksumAddress(
            OLD_SERVER_ADDRESSES[server_key]), abi=OLD_SERVER_ABI)
        tx_data = server_contract.functions.harvestAndBridge().build_transaction({
            "chainId": 1,
            "from": OPS_ADDRESS,
            "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
        })
        tx = w3.eth.account.sign_transaction(tx_data, private_key=OPS_PK)
        tx_hash = w3.eth.send_raw_transaction(tx.rawTransaction)

        try:
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        except:
            print(
                f"Transaction taking longer than expected, waiting 3 minutes: {tx_hash.hex()}")
            time.sleep(180)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        logs = server_contract.events.BridgedSushi(
        ).processReceipt(tx_receipt, errors=DISCARD)
        print(f"Server for {server_key} served in tx: {tx_hash.hex()}")
        print(
            f"Sushi Harvested & Bridged: {logs[0]['args']['amount'] / 1e18} SUSHI")


def bridge_eoa_servers(w3):
    return


def bridge_nodata_servers(w3):
    for server_key in NO_DATA_SERVER_ADDRESSES:
        print(f"Serving {server_key} Server...")
        server_contract = w3.eth.contract(w3.toChecksumAddress(
            NO_DATA_SERVER_ADDRESSES[server_key]), abi=DATA_SERVER_ABI)
        tx_data = server_contract.functions.bridge('0x').build_transaction({
            "chainId": 1,
            "from": OPS_ADDRESS,
            "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
        })
        tx = w3.eth.account.sign_transaction(tx_data, private_key=OPS_PK)
        tx_hash = w3.eth.send_raw_transaction(tx.rawTransaction)

        try:
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        except:
            print(
                f"Transaction taking longer than expected, waiting 3 minutes: {tx_hash.hex()}")
            time.sleep(180)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        logs = server_contract.events.BridgedSushi(
        ).processReceipt(tx_receipt, errors=DISCARD)
        print(f"Server for {server_key} served in tx: {tx_hash.hex()}")
        print(
            f"Sushi Harvested & Bridged: {logs[0]['args']['amount'] / 1e18} SUSHI")


def bridge_data_servers(w3):
    for server_key in DATA_SERVER_ADDRESS:
        match server_key:
            case "arbitrum":
                bridge_arbitrum(w3)
            # case "arbitrum-nova":
            #    serve_nova()
            # case "boba":
            #    serve_boba()
            # case "metis":
            #    serve_metis()
            case _:
                return


def bridge_arbitrum(w3):
    print(f"Serving arbitrum Server...")
    server_contract = w3.eth.contract(w3.toChecksumAddress(
        DATA_SERVER_ADDRESS["arbitrum"]), abi=DATA_SERVER_ABI)
    l2_transfer_gas_limit = 96190
    gas_price_bid = gas_price_arbitrum()
    max_submission_fee = get_arbitrum_retryable_submission_fee()
    eth_to_send = (l2_transfer_gas_limit * gas_price_bid) / \
        1e16 * 0.6 + (l2_transfer_gas_limit * gas_price_bid) / 1e16
    extra_data = encode(['uint256', 'bytes'], [
                        max_submission_fee, Web3.toBytes(text='')])[:-32]
    bridge_data = encode(['address', 'uint256', 'uint256', 'bytes'], [
        OPS_ADDRESS, l2_transfer_gas_limit, gas_price_bid, extra_data])

    tx_data = server_contract.functions.harvestAndBridge(Web3.toHex(bridge_data)).build_transaction({
        "chainId": 1,
        "from": OPS_ADDRESS,
        "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
        "value": Web3.toWei(eth_to_send, 'ether')
    })
    tx = w3.eth.account.sign_transaction(tx_data, private_key=OPS_PK)
    tx_hash = w3.eth.send_raw_transaction(tx.rawTransaction)
    try:
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    except:
        print(
            f"Transaction taking longer than expected, waiting 3 minutes: {tx_hash.hex()}")
        time.sleep(180)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    logs = server_contract.events.BridgedSushi(
    ).processReceipt(tx_receipt, errors=DISCARD)
    print(f"Server for arbitrum served in tx: {tx_hash.hex()}")
    print(
        f"Sushi Harvested & Bridged: {logs[0]['args']['amount'] / 1e18} SUSHI")


if __name__ == "__main__":
    # try:
    main()
    # except Exception as err:
    #    message = f"Task #{TASK_INDEX}, " \
    #        + f"Attempt #{TASK_ATTEMPT} failed: {str(err)}"
    #    print(json.dumps({"message": message, "severity": "ERROR"}))
    #    sys.exit(1)  # Retry Job Task by exiting the process
