import json
from web3 import Web3, HTTPProvider
from collections import defaultdict
import os
import sys

networks = [
    'arbitrum',
    'avalanche',
    'boba',
    'bsc',
    'ethereum',
    'fantom',
    'nova',
    'optimism',
    'polygon',
]

RPC_URL = {
    'arbitrum': 'https://rpc.ankr.com/arbitrum',
    'avalanche': 'https://avalanche.public-rpc.com',
    'boba': 'https://mainnet.boba.network',
    'bsc': 'https://bsc-dataseed.binance.org',
    'ethereum': 'https://eth.llamarpc.com',
    'fantom': 'https://1rpc.io/ftm',
    'nova': 'https://nova.arbitrum.io/rpc',
    'optimism': 'https://endpoints.omniatech.io/v1/op/mainnet/public',
    'polygon': 'https://polygon-rpc.com',
}

MERKLE_ADDRESS = {
    'arbitrum': '0x66343844d77B0805b942efFE6575a852b341Ba18',
    'avalanche': '0x9c56E5FC69C8cC7A19EDB0f1881b2Da0695988C9',
    'boba': '0x3706192DaA094E01a6b83378eAE15f697ED86365',
    'bsc': '0x4cFe5Ee193075C7e9FAD102cE87AEa5EF2025B6b',
    'ethereum': '0x049E1C6b35cD02d1fb2c62325A5FE9eA7E3Bc96C',
    'fantom': '0x5FeaE0Cedc9515784Df32C8779242FE8677776e6',
    'nova': '0x2eba324dB22b0dDeEFB5FFD0FF97631A35EFb8bB',
    'optimism': '0xE6E84929fd0269034BeaEB5c601C2b6C36E7a8B5',
    'polygon': '0xeaD6bD491457f3Aa7dbcb079FaAc93329837ABb0',
}

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)),
                 "./abis/SushiFundsReturner.json")
) as f:
    MERKLE_ABI = json.load(f)

data_to_dump = {}

for network in networks:
    w3 = Web3(Web3.HTTPProvider(RPC_URL[network]))
    merkle_contract = w3.eth.contract(
        address=MERKLE_ADDRESS[network], abi=MERKLE_ABI)

    print(network)
    tree_file = './data/trees/' + network + '-tree.json'

    # Load tree data
    with open(tree_file, 'r') as file:
        tree_data = json.load(file)

    unclaimed_users = []

    # Check isClaimed for each user
    for claim in tree_data['claims']:
        user = claim['user']
        index = claim['index']
        is_claimed = merkle_contract.functions.isClaimed(index).call()
        if not is_claimed:
            unclaimed_users.append(user)

    data_to_dump[network] = unclaimed_users

with open('./data/unclaimed_users.json', 'w') as file:
    json.dump(data_to_dump, file)
