import argparse
import requests
import json
from datetime import datetime, timedelta
from utils.graph_data import (
    fetch_swaps_data_classic,
    fetch_swaps_data_trident,
    fetch_swaps_data_v3,
    fetch_mint_data_v3,
    fetch_routes,
    fetch_v3_current_prices,
    fetch_v2_current_prices,
)
from utils.config import (
    CLASSIC_AMM_SUBGRAPH,
    TRIDENT_AMM_SUBGRAPH,
    V3_AMM_SUBGRAPH,
    WRAPPED_NATIVE_ADDRESS,
)


def pull_swaps_amms(timestamp_start, timestamp_end):
    print("Pulling swap data...")

    users_list = []

    print("Pulling data from classic AMM graph endpoints...")
    for network in CLASSIC_AMM_SUBGRAPH:
        swaps = fetch_swaps_data_classic(network, timestamp_start, timestamp_end)
        print(f"Found {len(swaps)} swaps on {network}...")
        users_list += [swap["sender"] for swap in swaps]
        # print(swaps)

    print("Pulling data from trident AMM graph endpoints...")
    for network in TRIDENT_AMM_SUBGRAPH:
        swaps = fetch_swaps_data_trident(network, timestamp_start, timestamp_end)
        print(f"Found {len(swaps)} swaps on {network}...")
        users_list += [swap["sender"] for swap in swaps]
        # print(swaps)

    print("Pulling data from v3 AMM graph endpoints...")
    for network in V3_AMM_SUBGRAPH:
        swaps = fetch_swaps_data_v3(network, timestamp_start, timestamp_end)
        print(f"Found {len(swaps)} swaps on {network}...")
        users_list += [swap["sender"] for swap in swaps]
        # print(swaps)

    print("Done!")

    users_list = list(set(users_list))

    # save to file
    with open("./data/users.txt", "w") as f:
        for user in users_list:
            f.write(f"{user}\n")

    print(f"Found {len(users_list)} unique users.")

def pull_swaps(network, token_addresses, minUSDAmount, timestamp_start, timestamp_end):
    print("Pulling swap data...")
    
    routes = fetch_routes(network, timestamp_start, timestamp_end)
    print(f"Found {len(routes)} routes...")

    # filter out routes that don't match token_addresses in the tokenIn or tokenOut
    if (WRAPPED_NATIVE_ADDRESS[network] in token_addresses):
        filtered_token_addresses = token_addresses + ['0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee']
        routes = [route for route in routes if route["tokenIn"] in filtered_token_addresses or route["tokenOut"] in filtered_token_addresses]
    else:
        routes = [route for route in routes if route["tokenIn"] in token_addresses or route["tokenOut"] in token_addresses] 

    print("Pulling pricing data...")
    prices = fetch_v3_current_prices(network, token_addresses)
    #prices_v2 = fetch_v2_current_prices(network, token_addresses)

    # replace tokenIn and tokenOut with WRAPPED_NATIVE_ADDRESS if native address
    for route in routes:
        if route["tokenIn"] == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
            route["tokenIn"] = WRAPPED_NATIVE_ADDRESS[network]
        if route["tokenOut"] == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
            route["tokenOut"] = WRAPPED_NATIVE_ADDRESS[network]

    filtered_minAmount_routes = []
    for route in routes:
        try:
            if route["tokenIn"] in token_addresses:
                amountUSD = (float(route["amountIn"]) / (10 ** float(prices[route["tokenIn"]]["decimals"]))) * float(prices[route["tokenIn"]]["usdPrice"])
                #if amountUSD == 0:
                    # check v2 price
                #    amountUSD = (float(route["amountIn"]) / (10 ** float(prices_v2[route["tokenIn"]]["decimals"]))) * float(prices_v2[route["tokenIn"]]["usdPrice"])
                if amountUSD >= minUSDAmount:
                    filtered_minAmount_routes.append(route)
            elif route["tokenOut"] in token_addresses:
                amountUSD = (float(route["amountOut"]) / (10 ** float(prices[route["tokenOut"]]["decimals"]))) * float(prices[route["tokenOut"]]["usdPrice"])
                #if amountUSD == 0:
                #    amountUSD = (float(route["amountOut"]) / (10 ** float(prices_v2[route["tokenOut"]]["decimals"]))) * float(prices_v2[route["tokenOut"]]["usdPrice"])
                if amountUSD >= minUSDAmount:
                    filtered_minAmount_routes.append(route)
        except:
            amountUSD = 0
    user_addresses = [
        route["from"]
        for route in filtered_minAmount_routes
    ]

    user_addresses = list(set(user_addresses))
    
    swaps_output_file_path = "./data/" + network + "-swaps" + "-" + str(timestamp_start) + "-" + str(timestamp_end) + ".txt"
    with open(swaps_output_file_path, "w") as f:
        for user in user_addresses:
            f.write(f"{user}\n")

def pull_mints(network, minUSD, timestamp_start, timestamp_end):
    print("Pulling mint data...")
    mints = fetch_mint_data_v3(network, timestamp_start, timestamp_end)
    print(f"Found {len(mints)} mints...")  

    user_addresses = [
        mint["origin"]
        for mint in mints
        if float(mint["amountUSD"]) >= minUSD
    ]

    user_addresses = list(set(user_addresses))

    mints_output_file_path = "./data/" + network + "-mints" + "-" + str(timestamp_start) + "-" + str(timestamp_end) + ".txt"
    with open(mints_output_file_path, "w") as f:
        for user in user_addresses:
            f.write(f"{user}\n")
    
    #print(user_addresses)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", help="Start timestamp")
    parser.add_argument("--end", help="End timestamp")
    args = parser.parse_args()

    #pull_swaps_amms(args.start, args.end)

    # ethereum - v3 mints & swaps
    pull_swaps(
        "ethereum", # network
        [
            "", # weth
            "", # sushi
            "", # wbtc
            "", # usdc
            "", # usdt
            "", #dai
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("ethereum", 10, 1693008000, 1693573200)

    # arbitrum - v3 mints & swaps
    pull_swaps(
        "arbitrum", # network
        [
            "0x82af49447d8a07e3bd95bd0d56f35241523fbab1", # weth
            "0xd4d42f0b6def4ce0383636770ef773390d85c61a", # sushi
            "0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f", # wbtc
            "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8", # usdc.e
            "0xaf88d065e77c8cc2239327c5edb3a432268e5831", # usdc
            "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9", # usdt
            "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1", # dai
            "0xfea7a6a0b346362bf88a9e4a88416b77a57d6c2a", # mim
            "0x912ce59144191c1204e64559fe8253a0e49e6548", # arb
            "0x6c2c06790b3e3e3c38e12ee22f8183b37a13ee55", # dpx
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("arbitrum", 10, 1693008000, 1693573200)

    # base - v3 mints & swaps
    pull_swaps(
        "base",
        [
            "0x8544fe9d190fd7ec52860abbf45088e81ee24a8c",
            "0x4200000000000000000000000000000000000006",
            "0x27d2decb4bfc9c76f0309b8E88dec3a601fe25a8",
            "0x0fa70e156cd3b03ac4080bfe55bd8ab50f5bcb98",
            "0xeb466342c4d449bc9f53a865d5cb90586f405215",
            "0x23ee2343b892b1bb63503a4fabc840e0e2c6810f",
            "0x22dc834c3ff3e45f484bf24B9b07b851b981900f",
            "0xe1f9ac62a2f34881f6fe0f84322de9d7024c2b8e",
            "0x966053115156a8279a986ed9400ac602fb2f5800",
            "0xd54a26aca1e4055ce99499945ff6a8b52d163d5a",
            "0x50c5725949a6f0c72e6c4a641f24049a917db0cb",
            "0xc2106ca72996e49bbadcb836eec52b765977fd20",
        ],
        10,
        1693008000,
        1693573200
    )
    pull_mints("base", 10, 1693008000, 1693573200)

    # polygon - v3 mints & swaps
    pull_swaps(
        "polygon", # network
        [
            "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270", # wmatic
            "0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6", # wbtc
            "0x0b3f868e0be5597d5db7feb59e1cadbb0fdda50a", # sushi
            "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", # usdc
            "0xc2132d05d31c914a87c6611c10748aeb04b58e8f", # usdt
            "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063", #dai
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("polygon", 10, 1693008000, 1693573200)

    # optimism - v3 mints & swaps
    pull_swaps(
        "optimism", # network
        [
            "0x4200000000000000000000000000000000000006", # weth
            "0x4200000000000000000000000000000000000042", # op
            "0x68f180fcce6836688e9084f035309e29bf0a2095", # wbtc
            "0x7f5c764cbc14f9669b88837ca1490cca17c31607", # usdc
            "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58", # usdt
            "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1", #dai
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("optimism", 10, 1693008000, 1693573200)

    # bsc - v3 mints & swaps
    pull_swaps(
        "bsc", # network
        [
            "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c", # wbnb
            "0x524bc91dc82d6b90ef29f76a3ecaabafffd490bc", # usdt
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("bsc", 10, 1693008000, 1693573200)
    
    # thundercore - v3 mints & swaps
    pull_swaps(
        "thundercore", # network
        [
            "0x413cefea29f2d07b8f2acfa69d92466b9535f717", # wTT
            "0x6576bb918709906dcbfdceae4bb1e6df7c8a1077", # TT-ETH
            "0x22e89898a04eaf43379beb70bf4e38b1faf8a31e", # TT-USDC
            "0x4f3c8e20942461e2c3bdd8311ac57b0c222f2b82", # TT-USDT
            "0x18fb0a62f207a2a082ca60aa78f47a1af4985190", # TT-WBTC
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("thundercore", 10, 1693008000, 1693573200)

    # gnosis - v3 mints & swaps
    pull_swaps(
        "gnosis", # network
        [
            "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d", # wxdai
            "0x9c58bacc331c9aa871afd802db6379a98e80cedb", # gno
            "0x6a023ccd1ff6f2045c3309768ead9e68f978f6e1", # weth
            "0xddafbb505ad214d7b80b1f830fccc89b60fb7a83", # usdc
            "0x4ecaba5870353805a9f068101a40e0f32ed605c6", # usdt
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("gnosis", 10, 1693008000, 1693573200)

    # avalanche - v3 mints & swaps
    pull_swaps(
        "avalanche", # network
        [
            "0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7", # wavax
            "0x49d5c2bdffac6ce2bfdb6640f4f80f226bc10bab", # weth.e
            "0x50b7545627a5162f82a992c33b87adc75187b218", # wbtc.e
            "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e", # usdc
            "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7", # usdt
            "0xd586e7f844cea2f87f50152665bcbc2c279d8d70", # DAI.e
            "0x130966628846bfd36ff31a822705796e8cb8c18d", # mim
            "0xD24C2Ad096400B6FBcd2ad8B24E7acBc21A1da64", # frax
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("avalanche", 10, 1693008000, 1693573200)

    # fantom - v3 mints & swaps
    pull_swaps(
        "fantom", # network
        [
            "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83", # wftm
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("fantom", 10, 1693008000, 1693573200)

    # nova - v3 mints & swaps
    pull_swaps(
        "nova", # network
        [
            "0x722e8bdd2ce80a4422e880164f2079488e115365", # weth
            "0xf823c3cd3cebe0a1fa952ba88dc9eef8e0bf46ad", # arb
            "0x750ba8b76187092b0d1e87e28daaf484d1b5273b", # usdc
            "0x1d05e4e72cd994cdf976181cfb0707345763564d", # wbtc
            "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1", # dai
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("nova", 10, 1693008000, 1693573200)

    # harmony - skip

    # metis - needs rp subgraph, no v3 mints
    
    # kava - needs rp subgraph, no v3 mints

    # bttc - needs rp subgraph, no v3 mints

    # boba - v3 mints & swaps
    pull_swaps(
        "boba", # network
        [
            "0xdeaddeaddeaddeaddeaddeaddeaddeaddead0000", # weth
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("boba", 10, 1693008000, 1693573200)
    
    # celo - swaps
    '''pull_swaps(
        "celo", # network
        [
            "0x471ece3750da237f93b8e339c536989b8978a438", # wcelo
            "", # weth
            "", # usdc
            "", # usdt
            "", # dai
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )'''

    # moonriver - v3 mints & swaps
    pull_swaps(
        "moonriver", # network
        [
            "0x98878b06940ae243284ca214f92bb71a2b032b8a", # wmovr
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("moonriver", 10, 1693008000, 1693573200)

    # zkevm - v3 mints & needs rp subgraph
    '''pull_swaps(
        "zkevm", # network
        [
            "0x4f9a0e7fd2bf6067db6994cf12e4495df938e6e9", # weth
            "0xa2036f0538221a77a3937f1379699f44945018d0", # wmatic
            "0xa8ce8aee21bc2a48a5ef670afcc9274c7bbbc035", # usdc
            "0x1e4a5963abfd975d8c9021ce480b42188849d41d", # usdt
            "0xea034fb02eb1808c2cc3adbc15f447b93cbe08e1", # wbtc
            "0xc5015b9d9161dca7e18e32f6f25c4ad850731fd4", # dai
        ], # tokens to whitelist
        10, # usd value
        1693008000, # start timestamp
        1693573200, # end timestamp
    )
    pull_mints("zkevm", 10, 1693008000, 1693573200)'''

    # core - v3 mints & swaps
    pull_swaps(
        "core",
        [
            "0x204e2d49b7cda6d93301bcf667a2da28fb0e5780",
            "0x40375c92d9faf44d2f9db9bd9ba41a3317a2404f",
            "0x900101d06a7426441ae63e9ab3b9b0f63be145f1",
            "0xa4151b2b3e269645181dccf2d426ce75fcbdeca9",
        ],
        10,
        1693008000,
        1693573200
    )
    pull_mints("core", 5, 1693008000, 1693573200)
    