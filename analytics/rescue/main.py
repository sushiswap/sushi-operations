import csv
import json
import os
from web3 import Web3, HTTPProvider
from decimal import Decimal, getcontext


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

key_mapping = {
    "token": "ContractAddress",
    "user": "From",
    "receiver": "To",
    "value": "TokenValue",
    "txHash": "Txhash"
}

ignore_token_list = {
    "arbitrum": [
        "0xb7d927a50531f9b3c43dc8d73033e765b24bf316",
        "0x37932bb72336462a052d7da588c75e32afa1cedf",
        "0x76f27f78554a6b6e0a49d49ccbf0691f7d648a50",
        "0x2e516ba5bf3b7ee47fb99b09eadb60bde80a82e0",
        "0x74ebb8e8d0b0cc65f06040eb0f77b5da0e33ffee",
    ],
    "avalanche": [],
    "boba": [],
    "bsc": [
        "0xd048b4c23af828e5be412505a51a8dd7b37782dd"
    ],
    "ethereum": [
        "0x9ea3b5b4ec044b70375236a281986106457b20ef"
    ],
    "fantom": [],
    "nova": [],
    "optimism": [],
    "polygon": []
}

decimal_token_book = {
    "arbitrum": {
        "0x50b871fb5bba2895425e5fc6eba219197f21d6d5": 18,
        "0x912ce59144191c1204e64559fe8253a0e49e6548": 18,
        "0xd3c66e09a66eb90879768e81971ce2c3f83ceeef": 9,
        "0xbc0a588120ab8b913436d342a702c92611c9af6a": 18,
        "0x6e0efbb4de17eec00fba09a14ccac2d92b0ac6b3": 18,
        "0xe78987ba38658607358d054224fd1580d1a5ad13": 9,
        "0xee9857de0e55d4a54d36a5a5a73a15e57435fdca": 18,
        "0xd4d42f0b6def4ce0383636770ef773390d85c61a": 18,
        "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8": 6,
        "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9": 6
    },
    "avalanche": {
        "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e": 6
    },
    "boba": {},
    "bsc": {
        "0xe9e7cea3dedca5984780bafc599bd69add087d56": 18,
        "0x986cdf0fd180b40c4d6aeaa01ab740b996d8b782": 18,
        "0x947950bcc74888a40ffa2593c5798f11fc9124c4": 18
    },
    "ethereum": {
        "0x0f2d719407fdbeff09d87557abb7232601fd9f29": 18,
        "0x767fe9edc9e0df98e07454847909b5e959d7ca0e": 18,
        "0xe60779cc1b2c1d0580611c526a8df0e3f870ec48": 18,
        "0x4c3a8eceb656ec63eae80a4ebd565e4887db6160": 18,
        "0xdac17f958d2ee523a2206206994597c13d831ec7": 6,
        "0xd417144312dbf50465b1c641d016962017ef6240": 18,
        "0xcd1de9fbbf6c5be46c748f862a5396991ab892ee": 9,
        "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": 18
    },
    "fantom": {
        "0x04068da6c83afcfa0e13ba15a6696662335d5b75": 6
    },
    "nova": {},
    "optimism": {
        "0x4200000000000000000000000000000000000042": 18,
        "0x7f5c764cbc14f9669b88837ca1490cca17c31607": 6,
        "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58": 6,
        "0x8c6f28f2f1a3c87f0f938b96d27520d9751ec8d9": 18,
        "0x296f55f8fb28e498b858d0bcda06d955b2cb3f97": 18
    },
    "polygon": {}
}

with open(
    os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "./abis/ERC20.json")
) as f:
    ERC20_ABI = json.load(f)


for network in networks:
    print(network)
    csv_file = './data/input/' + network + '-token-transfers.csv'
    json_file = './data/output/' + network + '-token-claims.json'

    columns_to_keep = [
        'ContractAddress',
        'From',
        'To',
        'TokenValue',
        'TxHash',
    ]

    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]

        renamed_rows = []
        for row in rows:
            if row['ContractAddress'] in ignore_token_list[network]:
                continue
            renamed_row = {new_key: row[old_key]
                           for new_key, old_key in key_mapping.items()}
            renamed_rows.append(renamed_row)

        for row in renamed_rows:
            row['chain'] = network

        # grab decimals and convert to BigNumber
        w3 = Web3(HTTPProvider(rpcs[network]))
        for row in renamed_rows:
            token = row['token']

            if token in decimal_token_book[network]:
                decimals = decimal_token_book[network][token]
                row['value'] = str(int(Decimal(row['value'].replace(
                    ',', '')) * Decimal(10 ** decimals)))
                continue

            try:
                contract = w3.eth.contract(
                    address=w3.toChecksumAddress(token), abi=ERC20_ABI)
                decimals = contract.functions.decimals().call()
                decimal_token_book[network][token] = decimals

                row['value'] = str(int(Decimal(row['value'].replace(
                    ',', '')) * Decimal(10 ** decimals)))
            except:
                print("Hard setting decimals for: ", token)
                row['value'] = str(int(Decimal(row['value'].replace(
                    ',', '')) * Decimal(10 ** 18)))

        # print(renamed_rows)

        with open(json_file, mode='w', encoding='utf-8') as f:
            json.dump(renamed_rows, f, ensure_ascii=False, indent=1)
