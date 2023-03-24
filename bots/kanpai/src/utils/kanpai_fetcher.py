import requests
import json
from datetime import datetime, timedelta

WETH_ADDRESS = {
    "mainnet": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "arbitrum": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
}

EXCHANGE_ENDPOINTS = {
    "mainnet": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange",
    "arbitrum": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-arbitrum-backup",
}

MAKER_ADDRESS = {
    "mainnet": "0x5ad6211cd3fde39a9cecb5df6f380b8263d1e277",
    "arbitrum": "0xa19b3b22f29e23e4c04678c94cfc3e8f202137d8",
}


def pull_maker_data(chain, timestamp_start):
    maker_burns_query = """query($maker: String!, $ts: Int!, $last_id: String) {
      burns(first: 1000, where: {sender: $maker, timestamp_gte: $ts, id_gt: $last_id}) {
        id
        timestamp
        transaction {
          id
        }
        pair {
          token0 {
            id
          }
          token1 {
            id
          }
        }
        amount0
        amount1
        sender
      }
    }
    """

    maker_swaps_query = """query($maker: String!, $ts: Int!, $last_id: String) {
      swaps(first: 1000, where: {sender: $maker, timestamp_gte: $ts, id_gt: $last_id}) {
        id
        transaction {
          id
        }
        pair {
          token0 {
            id
          }
          token1 {
            id
          }
        }
        sender
        amount0In
        amount1In
        amount0Out
        amount1Out
      }
    }
    """

    # fetch burns
    last_id = ""
    burns = []
    while True:
        variables = {
            "maker": MAKER_ADDRESS[chain],
            "ts": int(timestamp_start),
            "last_id": last_id,
        }
        result_burns = requests.post(
            EXCHANGE_ENDPOINTS[chain],
            json={"query": maker_burns_query, "variables": variables},
        )
        data_burns = json.loads(result_burns.text)

        if len(data_burns["data"]["burns"]) == 0:
            break

        burns += data_burns["data"]["burns"]
        last_id = burns[-1]["id"]

    last_id = ""
    swaps = []
    while True:
        variables = {
            "maker": MAKER_ADDRESS[chain],
            "ts": int(timestamp_start),
            "last_id": last_id,
        }
        result_swaps = requests.post(
            EXCHANGE_ENDPOINTS[chain],
            json={"query": maker_swaps_query, "variables": variables},
        )
        data_swaps = json.loads(result_swaps.text)

        if len(data_swaps["data"]["swaps"]) == 0:
            break

        swaps += data_swaps["data"]["swaps"]
        last_id = swaps[-1]["id"]

    return burns, swaps


def fetch_kanpai_data():
    print("Pulling data from exchange graph endpoint...")

    dates_to_check = {
        "start_of_year": datetime(2023, 1, 1),
        "month_before": datetime.now() - timedelta(30),
        "week_before": datetime.now() - timedelta(7),
        "day_before": datetime.now() - timedelta(1),
    }

    weth_amounts = {
        "start_of_year": 0,
        "month_before": 0,
        "week_before": 0,
        "day_before": 0,
    }

    for network in WETH_ADDRESS:
        for date in dates_to_check:
            burns, swaps = pull_maker_data(network, dates_to_check[date].timestamp())

            weth_burned = 0
            for burn in burns:
                if burn["pair"]["token0"]["id"] == WETH_ADDRESS[network]:
                    weth_burned += float(burn["amount0"])
                elif burn["pair"]["token1"]["id"] == WETH_ADDRESS[network]:
                    weth_burned += float(burn["amount1"])

            weth_amounts[date] += weth_burned

            weth_swapped = 0
            for swap in swaps:
                if (swap["pair"]["token0"]["id"] == WETH_ADDRESS[network]) and (
                    float(swap["amount0Out"]) > 0
                ):
                    weth_swapped += float(swap["amount0Out"])
                elif (swap["pair"]["token1"]["id"] == WETH_ADDRESS[network]) and (
                    float(swap["amount1Out"]) > 0
                ):
                    weth_swapped += float(swap["amount1Out"])

            weth_amounts[date] += weth_swapped

    for date in weth_amounts:
        print(f"Treasury earned {weth_amounts[date]} WETH since {date}")

    return weth_amounts
