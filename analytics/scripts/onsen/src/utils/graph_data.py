import requests
import json

EXCHANGE_ENDPOINTS = {
    "arbitrum": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-arbitrum-backup",
}


def fetch_pair_day_data(chain, pair, timestamp_start, timestamp_end):
    pair_day_data_query = """query($pair: String!, $ts_start: Int!, $ts_end: Int!, $last_id: String) {
      pairDayDatas(first: 1000, where: {pair: $pair, date_gte: $ts_start, date_lt: $ts_end, id_gt: $last_id}) {
        id
        date
        volumeUSD
      }
    }
    """

    # fetch pair day data
    last_id = ""
    pair_day_data = []
    while True:
        variables = {
            "pair": pair,
            "ts_start": int(timestamp_start),
            "ts_end": int(timestamp_end),
            "last_id": last_id,
        }
        result_days_data = requests.post(
            EXCHANGE_ENDPOINTS[chain],
            json={"query": pair_day_data_query, "variables": variables},
        )
        day_data = json.loads(result_days_data.text)

        if len(day_data["data"]["pairDayDatas"]) == 0:
            break

        pair_day_data += day_data["data"]["pairDayDatas"]
        last_id = pair_day_data[-1]["id"]

    return pair_day_data


def fetch_pair_info(chain, pair):
    pair_query = """query($pair: String!) {
      pair(id: $pair) {
        id
        token0 {
          id
        }
        token1 {
          id
        }
        reserve0
        reserve1
        totalSupply
        reserveETH
        reserveUSD
        token0Price
        token1Price
        volumeUSD
        untrackedVolumeUSD
        txCount
        liquidityProviderCount
      }
    }
    """

    variables = {"pair": pair}
    result_pair = requests.post(
        EXCHANGE_ENDPOINTS[chain], json={"query": pair_query, "variables": variables}
    )
    pair_data = json.loads(result_pair.text)

    return pair_data["data"]["pair"]
