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
    
    pull_swaps("thundercore", ["0x413cefea29f2d07b8f2acfa69d92466b9535f717"], 10, 1686009600, 1686628160)
    pull_mints("thundercore", 10, 1686009600, 1686628160)