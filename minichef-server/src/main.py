import sys, os
import json
import time
from web3 import Web3, HTTPProvider
from web3.logs import DISCARD
from web3.gas_strategies.time_based import fast_gas_price_strategy

from utils.gas import gas_price_mainnet, gas_price_arbitrum

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


def main():
  print("Running MiniChef Servers Job")
  print(f"Starting Task #{TASK_INDEX}, Atempt #{TASK_ATTEMPT}...")

  w3 = Web3(Web3.HTTPProvider(MAINNET_RPC_URL))
  w3.eth.set_gas_price_strategy(fast_gas_price_strategy)
  if not w3.isConnected:
    print("Could not connect to mainnet RPC")
    return RuntimeError

  if (w3.eth.gasPrice > 3e9 ):
    print(f"Gas price is too high: {w3.eth.gasPrice}")
    return RuntimeError

  print(f"Current block is: {w3.eth.blockNumber}")
  
  print("Serving Old MiniChef Servers...")
  bridge_old_servers(w3)

  print(f"Completed Task #{TASK_INDEX}.")

def bridge_old_servers(w3):
  with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "abis/OldServer.json")) as f:
    server_abi = json.load(f)

  for server_key in OLD_SERVER_ADDRESSES:
    print(f"Serving {server_key} Server...")
    server_contract = w3.eth.contract(w3.toChecksumAddress(OLD_SERVER_ADDRESSES[server_key]), abi=server_abi)
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
      print(f"Transaction taking longer than expected, waiting 3 minutes: {tx_hash.hex()}")
      time.sleep(180)
      tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    logs = server_contract.events.BridgedSushi().processReceipt(tx_receipt, errors=DISCARD)
    print(f"Server for {server_key} served in tx: {tx_hash.hex()}")
    print(f"Sushi Harvested & Bridged: {logs[0]['args']['amount'] / 1e18} SUSHI")

def bridge_eoa_servers():
  return

def bridge_nondata_servers():
  return

def bridge_data_servers():
  return


if __name__ == "__main__":
  try:
    main()
  except Exception as err:
    message = f"Task #{TASK_INDEX}, " \
      + f"Attempt #{TASK_ATTEMPT} failed: {str(err)}"
    print(json.dumps({"message": message, "severity": "ERROR"}))
    sys.exit(1)  # Retry Job Task by exiting the process
