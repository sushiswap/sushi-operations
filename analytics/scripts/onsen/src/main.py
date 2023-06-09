import argparse
import requests
import json
from datetime import datetime, timedelta
from utils.graph_data import fetch_pair_day_data, fetch_pair_info


def main(network, pair):
    print("Pulling data from exchange graph endpoint...")

    dates_to_check = {
        "start_of_year": datetime(2023, 1, 1),
        "month_before": datetime.now() - timedelta(30),
        "week_before": datetime.now() - timedelta(7),
        "day_before": datetime.now() - timedelta(1),
    }

    # fetch pair info data
    pair_info = fetch_pair_info(network, pair)

    #
    for date in dates_to_check:
        day_data = fetch_pair_day_data(
            network,
            pair,
            dates_to_check[date].timestamp(),
            datetime.now().timestamp(),
        )

        day_volume = 0
        for day in day_data:
            day_volume += float(day["volumeUSD"])

        print(
            f"Pair {pair} traded {day_volume} USD since {dates_to_check[date]} on {network}"
        )

    print(f"Pair Total Volume: {pair_info['volumeUSD']} USD on {network}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", help="Network")
    parser.add_argument("--pair", help="Pair address")
    args = parser.parse_args()

    main(args.network, args.pair)
