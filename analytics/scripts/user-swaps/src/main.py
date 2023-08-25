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

    # replace tokenIn and tokenOut with WRAPPED_NATIVE_ADDRESS if native address
    for route in routes:
        if route["tokenIn"] == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
            route["tokenIn"] = WRAPPED_NATIVE_ADDRESS[network]
        if route["tokenOut"] == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
            route["tokenOut"] = WRAPPED_NATIVE_ADDRESS[network]

    filtered_minAmount_routes = []
    for route in routes:
        if route["tokenIn"] in token_addresses:
            amountUSD = (float(route["amountIn"]) / (10 ** float(prices[route["tokenIn"]]["decimals"]))) * float(prices[route["tokenIn"]]["usdPrice"])
            if amountUSD >= minUSDAmount:
                filtered_minAmount_routes.append(route)
        elif route["tokenOut"] in token_addresses:
            amountUSD = (float(route["amountOut"]) / (10 ** float(prices[route["tokenOut"]]["decimals"]))) * float(prices[route["tokenOut"]]["usdPrice"])
            if amountUSD >= minUSDAmount:
                filtered_minAmount_routes.append(route)

    user_addresses = [
        route["from"]
        for route in filtered_minAmount_routes
    ]

    user_addresses = list(set(user_addresses))
    
    swaps_output_file_path = "./data/" + network + "-swaps" + "-" + str(timestamp_start) + "-" + str(timestamp_end) + ".txt"
    with open(swaps_output_file_path, "w") as f:
        for user in user_addresses:
            f.write(f"{user}\n")

    #print(user_addresses)

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

    '''
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
        1691107200,
        1692403200
    )
    pull_mints("base", 10, 1691107200, 1692403200)
    '''
    
    pull_swaps(
        "core",
        [
            "0x204e2d49b7cda6d93301bcf667a2da28fb0e5780",
            "0x40375c92d9faf44d2f9db9bd9ba41a3317a2404f",
            "0x900101d06a7426441ae63e9ab3b9b0f63be145f1",
            "0xa4151b2b3e269645181dccf2d426ce75fcbdeca9",
        ],
        10,
        1690934400,
        1692316800
    )
    pull_mints("core", 5, 1690934400, 1692316800)
    