import sys, os
import json
from web3 import Web3, HTTPProvider
from web3.gas_strategies.rpc import rpc_gas_price_strategy

from utils.gas import gas_price_mainnet, gas_price_arbitrum

# Retrieve job-defined env vars
TASK_INDEX = os.getenv("CLOUD_RUN_TASK_INDEX", 0)
TASK_ATTEMPT = os.getenv("CLOUD_RUN_TASK_ATTEMPT", 0)
# Retrieve user-defined env vars
MAINNET_RPC_URL = os.environ["MAINNET_RPC_URL"] 
OPS_ADDRESS = os.environ["OPS_ADDRESS"]
OPS_PK = os.environ["OPS_PK"]

SERVER_ADDRESSES = {
  "polygon": "0x3d0B3b816DC1e0825808F27510eF7Aa5E3136D75"
}


def main():
  print("Running MiniChef Servers Job")
  print(f"Starting Task #{TASK_INDEX}, Atempt #{TASK_ATTEMPT}...")

  w3 = Web3(Web3.HTTPProvider(MAINNET_RPC_URL))
  w3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
  if not w3.isConnected:
    print("Could not connect to mainnet RPC")
    return RuntimeError

  print(f"Current block is: {w3.eth.blockNumber}")
  

  print("Serving Polygon Server...")
  with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "abis/PolygonServer.json")) as f:
    server_abi = json.load(f)

  server_contract = w3.eth.contract(w3.toChecksumAddress(SERVER_ADDRESSES["polygon"]), abi=server_abi)
  tx_data = server_contract.functions.harvestAndBridge().build_transaction({
    "chainId": 1,
    "from": OPS_ADDRESS,
    "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
  })
  tx = w3.eth.account.sign_transaction(tx_data, private_key=OPS_PK)
  tx_hash = w3.eth.send_raw_transaction(tx.rawTransaction)
  tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
  logs = server_contract.events.BridgedSushi().processReceipt(tx_receipt)

  print(f"Polygon Server served in tx: {tx_hash.hex()}")
  print(f"Sushi Harvested & Bridged: {logs[0]['value'] / 1e18}")

  print(f"Completed Task #{TASK_INDEX}.")



if __name__ == "__main__":
  try:
    main()
  except Exception as err:
    message = f"Task #{TASK_INDEX}, " \
      + f"Attempt #{TASK_ATTEMPT} failed: {str(err)}"
    print(json.dumps({"message": message, "severity": "ERROR"}))
    sys.exit(1)  # Retry Job Task by exiting the process
