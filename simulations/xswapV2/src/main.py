import sys
import os
import math
import time
import json
import argparse
from web3 import Web3, HTTPProvider
from eth_abi import encode
from dotenv import load_dotenv


from utils.config import (
    RPC_URLS,
    CHAIN_MAP,
    XSWAPV2_ADDRESSES,
    STARGATE_ADAPTER_ADDRESSES,
    SQUID_ADAPTER_ADDRESSES,
)

load_dotenv()

OPS_ADDRESS = os.environ["OPS_ADDRESS"]
OPS_PRIVATE_KEY = os.environ["OPS_PRIVATE_KEY"]

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)),
                 "abis/SushiXSwapV2.json")
) as f:
    XSWAP_V2_ABI = json.load(f)


with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)),
                 "abis/StargateAdapter.json")
) as f:
    STARGATE_ADAPTER_ABI = json.load(f)


def main():
    # basic test
    test_basic_bridge_arb_to_op()

    return


def test_basic_bridge_arb_to_op():
  # test basic bridge usdc from arbitrum to optimism test using stargate adapter

  w3 = Web3(HTTPProvider(RPC_URLS["arbitrum"]))
  if not w3.isConnected():
      print("Error: Web3 provider is not connected.")
      return

  xswap_contract = w3.eth.contract(
      w3.toChecksumAddress(XSWAPV2_ADDRESSES["arbitrum"]),
      abi=XSWAP_V2_ABI
  )

  stargate_adapter_contract = w3.eth.contract(
      w3.toChecksumAddress(STARGATE_ADAPTER_ADDRESSES["arbitrum"]),
      abi=STARGATE_ADAPTER_ABI
  )

  #if chain in ["mainnet", "arbitrum"]:
  last_block = w3.eth.get_block("latest")
  next_gas_price = math.ceil(last_block.get("baseFeePerGas") * 1.125)
    #else:
    #    next_gas_price = w3.eth.gas_price

  # bridge call
  '''
  BridgeParams
    address adapter
    address tokenIn
    uint256 amountIn
    address to
    bytes adapterData -> StargateTeleportParams
      uint16 dstChainId -> stargate dst chain id
      address token -> token getting bridged
      uint256 srcPoolId -> stargate src pool id
      uint256 dstPoolId -> stargate dst pool id
      uint256 amount -> amount to bridge
      uint256 amountMin -> amount to bridge minimum
      uint256 dustAmount -> native token to be received on dst chain
      address receiver -> the address to send the token to on dst chain
      address to -> the address to send tokens to on dst chain
      uint256 gas -> extra gas to be sent for dst chain operations
  '''
  adapter_bData = w3.toChecksumAddress("0xe2752b113f55373e86b5c13b6d7d1ad439c371dc")
  tokenIn_bData = w3.toChecksumAddress("0xff970a61a04b1ca14834a43f5de4533ebddb5cc8")
  amountIn_bData = 1000000 # 1 USDC
  to_bData = "0x0000000000000000000000000000000000000000"
  # adapterData
  dstChainId_aData = 111 # optimism
  token_aData = tokenIn_bData
  srcPoolId_aData = 1 # usdc pool
  dstPoolId_aData = 1 # usdc pool
  amount_aData = amountIn_bData
  amountMin_aData = 0
  dustAmount_aData = 0
  receiver_aData = w3.toChecksumAddress(OPS_ADDRESS) #w3.toChecksumAddress("0xc14ee6b248787847527e11b8d7cf257b212f7a9f") # op xswapv2
  to_aData =  w3.toChecksumAddress("0x0000000000000000000000000000000000000000")#w3.toChecksumAddress(OPS_ADDRESS)
  gas_aData = 0 #100000 # extra gas, since sending to xSwapV2 address need gas for send to wallet
  payload_data = Web3.toBytes(text="")

  # calculate gas needed for dst chain (op)
  gas_result = stargate_adapter_contract.functions.getFee(
      dstChainId_aData,
      1, # swap function type
      w3.toChecksumAddress(receiver_aData),
      gas_aData,
      dustAmount_aData,
      payload_data, # payload maybe should be address if receiver is xswapv2 contract?
  ).call()

  print(f"lz getFee result (wei): {gas_result}")

  total_gas_needed = math.ceil(gas_aData + gas_result[0] * 1.25) # 25% extra gas
  print(f"native needed: {Web3.fromWei(total_gas_needed, 'ether')}")

  adapter_params = encode(
      ["uint16", "address", "uint256", "uint256", "uint256", "uint256", "uint256", "address", "address", "uint256"],
      [dstChainId_aData, token_aData, srcPoolId_aData, dstPoolId_aData, amount_aData, amountMin_aData, dustAmount_aData, receiver_aData, to_aData, gas_aData]
  )

  bridge_params = encode(
      ["address", "address", "uint256", "address", "bytes"],
      [adapter_bData, tokenIn_bData, amountIn_bData, to_bData, adapter_params]
  )

  bridge_params_2 = (
      adapter_bData,
      tokenIn_bData,
      amountIn_bData,
      to_bData,
      adapter_params
  )

  gas_estimate = xswap_contract.functions.bridge(
      bridge_params_2,
      Web3.toBytes(text=""), # _swapPayload
      payload_data, # _payloadData
  ).estimate_gas(
    {
      "chainId": CHAIN_MAP['arbitrum'],
      "from": OPS_ADDRESS,
      "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
      "value": total_gas_needed
    }
  )

  print(f"xSwap gasEstimate: {gas_estimate}")

  tx_data = xswap_contract.functions.bridge(
      bridge_params_2,
      Web3.toBytes(text=""), # _swapPayload
      Web3.toBytes(text=""), # _payloadData
  ).build_transaction(
    {
      "chainId": CHAIN_MAP['arbitrum'],
      "from": OPS_ADDRESS,
      "nonce": w3.eth.get_transaction_count(OPS_ADDRESS),
      "value": total_gas_needed,
      "gas": gas_estimate,
      "maxFeePerGas": next_gas_price,
    }
  )

  tx = w3.eth.account.sign_transaction(tx_data, private_key=OPS_PRIVATE_KEY)
  tx_hash = w3.eth.send_raw_transaction(tx.rawTransaction)

  try:
    tx_receipt = w3.eth.wait_for_transaction_receipt(
      tx_hash, timeout=1200)
  except:
    print(
      f"Transaction taking longer than expected, waiting 3 minutes: {tx_hash.hex()}"
    )
    time.sleep(180)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
  
  print(f"Bridge executed successfully in tx: {tx_hash.hex()}")
  

  return


if __name__ == "__main__":
    

    main()
