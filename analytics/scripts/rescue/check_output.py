import json
import os
from web3 import Web3, HTTPProvider
from collections import defaultdict

rpcs = {
    'arbitrum': 'https://arb-mainnet-public.unifra.io',
    'avalanche': 'https://avalanche-c-chain.publicnode.com',
    'boba': 'https://mainnet.boba.network',
    'bsc': 'https://bsc.publicnode.com',
    'ethereum': 'https://eth.llamarpc.com',
    'fantom': 'https://rpc2.fantom.network',
    'nova': 'https://nova.arbitrum.io/rpc',
    'optimism': 'https://mainnet.optimism.io',
    'polygon': 'https://polygon.llamarpc.com',
}

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

WHITEHAT_ADDRESS = "0x74ebb8e8d0b0cc65f06040eb0f77b5da0e33ffee"
WHITEHAT_ADDRESS_FTM = "0x164f82ae0261ad2ad5f99b7a01d5fb80d4acc963"

with open(
    os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "./abis/ERC20.json")
) as f:
    ERC20_ABI = json.load(f)

for network in networks:
    if network == 'fantom':
        whitehat_address = WHITEHAT_ADDRESS_FTM
    else:
        whitehat_address = WHITEHAT_ADDRESS

    w3 = Web3(HTTPProvider(rpcs[network]))

    print(f"Checking Totals for {network}")
    print("-----------------------------------")

    json_file = './data/pre-tree-inputs/' + network + '-token-claims.json'
    with open(json_file, mode='r', encoding='utf-8') as f:
        data = json.load(f)

    sums_by_token = defaultdict(int)

    for entry in data:
        token = entry['token']
        amount = int(entry['value'])
        sums_by_token[token] += amount

    # Then check balanceOf on each token
    for token, amount in sums_by_token.items():
        try:
            contract = w3.eth.contract(
                address=w3.toChecksumAddress(token), abi=ERC20_ABI)
            balance = contract.functions.balanceOf(
                w3.toChecksumAddress(whitehat_address)).call()

            if balance != amount:
                print('---------------')
                print(
                    f"ERROR: {token} output file has {amount}, but contract shows {balance}")
                print('---------------')
        except:
            print('---------------')
            print(f"MANUAL CHECK REQUIRED: {token} ")
            print(f"amount from output: {amount}")
            print('---------------')

    # for token, amount in sums_by_token.items():
    #    print(f"{token}: {amount}")
