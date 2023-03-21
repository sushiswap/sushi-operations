import os

MAINNET_RPC_URL = os.environ["MAINNET_RPC_URL"]
ARBITRUM_RPC_URL = os.environ["ARBITRUM_RPC_URL"]

RPC_URL = {
    "mainnet": MAINNET_RPC_URL,
    "arbitrum": ARBITRUM_RPC_URL,
    "polygon": "https://polygon-rpc.com",
    "fantom": "https://1rpc.io/ftm",
    "boba": "https://mainnet.boba.network",
    "nova": "https://nova.arbitrum.io/rpc",
    "bsc": "https://bsc-dataseed.binance.org",
    "avax": "https://avalanche.public-rpc.com",
    "gnosis": "https://rpc.gnosischain.com",
    "celo": "https://forno.celo.org",
    "moonriver": "https://rpc.api.moonriver.moonbeam.network",
}

CHAIN_MAP = {
    "mainnet": 1,
    "arbitrum": 42161,
    "polygon": 137,
    "fantom": 250,
    "boba": 288,
    "nova": 42170,
    "bsc": 56,
    "avax": 43114,
    "gnosis": 100,
    "celo": 42220,
    "moonriver": 1285,
}

WETH_SERVER_ADDRESSES = {
    "mainnet": "0x5ad6211CD3fdE39A9cECB5df6f380b8263d1e277",
    "arbitrum": "0xa19b3b22f29E23e4c04678C94CFC3e8f202137d8",
    "polygon": "0xf1c9881be22ebf108b8927c4d197d126346b5036",
    "fantom": "0x194d47464deeafef3b599b81e2984306a315d422",
    "boba": "",
    "nova": "",
    "bsc": "0xe2d7460457f55e4786C69D2d3fa81978Bf8DD11C",
    "avax": "0x560C759A11cd026405F6f2e19c65Da1181995fA2",
    "gnosis": "0xa974B421d31DB37D6522Abf7783dcBadF39d21D1",
    "celo": "0x79eFe1049e8A95f1E11a216DE2DCa27b1E941Bfb",
    "moonriver": "0x1c8FA2f5f7520Eef45B7E4816687AF0e8E991760",
}

MIN_USD_VAL = {
    "mainnet": 100,
    "arbitrum": 10,
    "polygon": 10,
    "fantom": 10,
    "boba": 10,
    "nova": 10,
    "bsc": 10,
    "avax": 10,
    "gnosis": 10,
    "celo": 10,
    "moonriver": 10,
}

EXCHANGE_GRAPH_ENDPOINTS = {
    "mainnet": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-ethereum",
    "arbitrum": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-arbitrum-backup",
    "polygon": "https://api.thegraph.com/subgraphs/name/sushiswap/matic-exchange",
    "fantom": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-fantom",
    "boba": "https://api.thegraph.com/subgraphs/name/sushi-0m/sushiswap-boba",
    "nova": "https://subgraphs.sushi.com/subgraphs/name/sushi-0m/sushiswap-arbitrum-nova",
    "bsc": "https://api.thegraph.com/subgraphs/name/sushiswap/bsc-exchange",
    "avax": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-avalanche",
    "gnosis": "https://api.thegraph.com/subgraphs/name/sushiswap/xdai-exchange",
    "celo": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-celo",
    "moonriver": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-moonriver",
}

BASE_ADDRESS = {
    "mainnet": [
        "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
        "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
        "0xdac17f958d2ee523a2206206994597c13d831ec7",  # USDT
        "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
        "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",  # WBTC
        "0xd533a949740bb3306d119cc777fa900ba034cd52",  # CRV
        "0x853d955acef822db058eb8505911ed77f175b99e",  # FRAX
    ],
    "arbitrum": [
        "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",  # WETH
        "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8",  # USDC
        "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",  # USDT
        "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",  # DAI
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
    "fantom": [
        "0x74b23882a30290451a17c44f4f05243b6b58c76d",  # WETH
        "0x04068da6c83afcfa0e13ba15a6696662335d5b75",  # USDC
        "0x21be370d5312f44cb42ce377bc9b8a0cef1a4c83",  # WFTM
        "0x049d68029688eabf473097a2fc38ef61633a3c7a",  # USDT
    ],
    "boba": [],
    "nova": [],
    "bsc": [
        "0x55d398326f99059ff775485246999027b3197955",  # USDT
        "0x2170ed0880ac9a755fd29b2688956bd959f933f8",  # ETH
        "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",  # WBNB
        "0xe9e7cea3dedca5984780bafc599bd69add087d56",  # BUSD
    ],
    "avax": [
        "0xa7d7079b0fead91f3e65f86e8915cb59c1a4c664",  # USDC.e
        "0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7",  # WAVAX
        "0x49d5c2bdffac6ce2bfdb6640f4f80f226bc10bab",  # WETH.e
        "0x130966628846bfd36ff31a822705796e8cb8c18d",  # MIM
        "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",  # USDC
        "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7",  # USDt
        "0x0da67235dd5787d67955420c84ca1cecd4e5bb3b",  # wMEMO
        "0xd586e7f844cea2f87f50152665bcbc2c279d8d70",  # DAI.e
    ],
    "gnosis": [
        "0x6a023ccd1ff6f2045c3309768ead9e68f978f6e1",  # WETH
        "0xddafbb505ad214d7b80b1f830fccc89b60fb7a83",  # USDC
        "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",  # WXDAI
        "0x9c58bacc331c9aa871afd802db6379a98e80cedb",  # GNO
        "0x4ecaba5870353805a9f068101a40e0f32ed605c6",  # USDT
    ],
    "celo": [
        "0x765de816845861e75a25fca122bb6898b8b1282a",  # cUSD
        "0xef4229c8c3250c675f21bcefa42f58efbff6002a",  # USDC
        "0x471ece3750da237f93b8e339c536989b8978a438",  # CELO
        "0x122013fd7df1C6f636a5bb8f03108e876548b455",  # WETH
        "0xe4fe50cdd716522a56204352f00aa110f731932d",  # DAI
        "0x617f3112bf5397d0467d315cc709ef968d9ba546",  # USDT
        "0xd8763cba276a3738e6de85b4b3bf5fded6d6ca73",  # cEUR
    ],
    "moonriver": [
        "0x98878b06940ae243284ca214f92bb71a2b032b8a",  # wMOVR
        "0xf50225a84382c74cbdea10b0c176f71fc3de0c4d",  # wMOVR
        "0x639a647fbe20b6c8ac19e48e2de44ea792c62c5c",  # WETH
        "0xe3f5a90f9cb311505cd691a46596599aa1a0ad7d",  # USDC
        "0xb44a9b6905af7c801311e8f4e76932ee959c663c",  # USDT
    ],
}
