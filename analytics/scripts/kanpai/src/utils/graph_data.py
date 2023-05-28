import requests
import json


EXCHANGE_ENDPOINTS = {
    "mainnet": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange",
    "arbitrum": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-arbitrum-backup",
}

MAKER_ADDRESS = {
    "mainnet": "0x5ad6211cd3fde39a9cecb5df6f380b8263d1e277",
    "arbitrum": "0xa19b3b22f29e23e4c04678c94cfc3e8f202137d8",
}


def fetch_kanpai_data(chain, timestamp_start):
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
