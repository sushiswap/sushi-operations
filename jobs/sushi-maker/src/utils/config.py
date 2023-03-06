import os

MAINNET_RPC_URL = os.environ["MAINNET_RPC_URL"]
ARBITRUM_RPC_URL = os.environ["ARBITRUM_RPC_URL"]

RPC_URL = {
    "mainnet": MAINNET_RPC_URL,
    "arbitrum": ARBITRUM_RPC_URL,
    "polygon": "https://polygon-rpc.com",
}

CHAIN_MAP = {
    "mainnet": 1,
    "arbitrum": 42161,
    "polygon": 137,
}

WETH_SERVER_ADDRESSES = {
    "mainnet": "0x5ad6211CD3fdE39A9cECB5df6f380b8263d1e277",
    "arbitrum": "0xa19b3b22f29E23e4c04678C94CFC3e8f202137d8",
    "polygon": "0xf1c9881be22ebf108b8927c4d197d126346b5036",
}

MIN_USD_VA = {
    "mainnet": 100,
    "arbitrum": 10,
    "polygon": 10,
}

EXCHANGE_GRAPH_ENDPOINTS = {
    "mainnet": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-ethereum",
    "arbitrum": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-arbitrum-backup",
    "polygon": "https://api.thegraph.com/subgraphs/name/sushiswap/matic-exchange",
}

BASE_ADDRESS = {
    "mainnet": [
        "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
        "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
        "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
        "0xdac17f958d2ee523a2206206994597c13d831ec7",  # USDT
        "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",  # WBTC
        "0xd533a949740bb3306d119cc777fa900ba034cd52",  # CRV
        "0x853d955acef822db058eb8505911ed77f175b99e",  # FRAX
    ],
    "arbitrum": [
        "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",  # WETH
        "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8",  # USDC
        "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",  # DAI
        "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",  # USDT
        "0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f",  # WBTC
    ],
    "polygon": [
        "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619",  # WETH
        "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  # USDC
        "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",  # WMATIC
        "0xc2132d05d31c914a87c6611c10748aeb04b58e8f",  # USDT
        "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063",  # DAI
        "0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6",  # WBTC
        "0x45c32fa6df82ead1e2ef74d17b76547eddfaff89",  # FRAX
    ],
}
