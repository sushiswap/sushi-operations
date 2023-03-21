import argparse
import requests
import json
from datetime import datetime, timedelta
from utils.graph_data import fetch_kanpai_data


WETH_ADDRESS = {
    "mainnet": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "arbitrum": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
}


def main():
    print("Pulling data from exchange graph endpoint...")

    dates_to_check = {
        "start_of_year": datetime(2023, 1, 1),
        "month_before": datetime.now() - timedelta(30),
        "week_before": datetime.now() - timedelta(7),
    }

    weth_amounts = {
        "start_of_year": 0,
        "month_before": 0,
        "week_before": 0,
    }

    for network in WETH_ADDRESS:
        for date in dates_to_check:
            burns, swaps = fetch_kanpai_data(
                network, dates_to_check[date].timestamp())

            weth_burned = 0
            # print(f"There are {len(burns)} burns...")
            for burn in burns:
                if burn['pair']['token0']['id'] == WETH_ADDRESS[network]:
                    weth_burned += float(burn['amount0'])
                elif burn['pair']['token1']['id'] == WETH_ADDRESS[network]:
                    weth_burned += float(burn['amount1'])

            # print(
            #    f"Maker burned {weth_burned} WETH since {dates_to_check[date]} on {network}")
            weth_amounts[date] += weth_burned

            weth_swapped = 0
            # print(f"There are {len(swaps)} swaps...")
            for swap in swaps:
                if (swap['pair']['token0']['id'] == WETH_ADDRESS[network]) and (float(swap['amount0Out']) > 0):
                    weth_swapped += float(swap['amount0Out'])
                elif (swap['pair']['token1']['id'] == WETH_ADDRESS[network]) and (float(swap['amount1Out']) > 0):
                    weth_swapped += float(swap['amount1Out'])

            # print(
            #    f"Maker swapped for {weth_swapped} WETH since {dates_to_check[date]} on {network}")
            weth_amounts[date] += weth_swapped

    for date in weth_amounts:
        print(f"Treasury earned {weth_amounts[date]} WETH since {date}")


if __name__ == '__main__':
    main()
