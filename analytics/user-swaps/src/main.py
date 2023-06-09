import argparse
import requests
import json
from datetime import datetime, timedelta
from utils.graph_data import (
    fetch_swaps_data_classic,
    fetch_swaps_data_trident,
    fetch_swaps_data_v3,
)
from utils.config import (
    CLASSIC_AMM_SUBGRAPH,
    TRIDENT_AMM_SUBGRAPH,
    V3_AMM_SUBGRAPH,
)


def main(timestamp_start, timestamp_end):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", help="Start timestamp")
    parser.add_argument("--end", help="End timestamp")
    args = parser.parse_args()

    main(args.start, args.end)
