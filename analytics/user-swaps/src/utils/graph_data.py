import requests
import json

from utils.config import (
    CLASSIC_AMM_SUBGRAPH,
    TRIDENT_AMM_SUBGRAPH,
    V3_AMM_SUBGRAPH,
)


def fetch_swaps_data_classic(chain, timestamp_start, timestamp_end):
    swaps_query = """query($ts_start: Int!, $ts_end: Int!, $last_id: String) {
      swaps(first: 1000, where: {timestamp_gte: $ts_start, timestamp_lte: $ts_end, id_gt: $last_id}) {
        id
        pair
        sender
        timestamp
        amountUSD
      }
    }
    """

    # fetch swaps
    last_id = ""
    swaps = []
    while True:
        variables = {
            "ts_start": int(timestamp_start),
            "ts_end": int(timestamp_end),
            "last_id": last_id,
        }

        result_swaps = requests.post(
            CLASSIC_AMM_SUBGRAPH[chain],
            json={"query": swaps_query, "variables": variables},
        )
        data = json.loads(result_swaps.text)

        if len(data["data"]["swaps"]) == 0:
            break

        swaps += data["data"]["swaps"]
        last_id = swaps[-1]["id"]

    return swaps


def fetch_swaps_data_trident(chain, timestamp_start, timestamp_end):
    swaps_query = """query($ts_start: Int!, $ts_end: Int!, $last_id: String) {
      swaps(first: 1000, where: {timestamp_gte: $ts_start, timestamp_lte: $ts_end, id_gt: $last_id}) {
        id
        pair
        sender
        timestamp
        amountUSD
      }
    }
    """

    # fetch swaps
    last_id = ""
    swaps = []
    while True:
        variables = {
            "ts_start": int(timestamp_start),
            "ts_end": int(timestamp_end),
            "last_id": last_id,
        }

        result_swaps = requests.post(
            TRIDENT_AMM_SUBGRAPH[chain],
            json={"query": swaps_query, "variables": variables},
        )
        data = json.loads(result_swaps.text)

        if len(data["data"]["swaps"]) == 0:
            break

        swaps += data["data"]["swaps"]
        last_id = swaps[-1]["id"]

    return swaps


def fetch_swaps_data_v3(chain, timestamp_start, timestamp_end):
    swaps_query = """query($ts_start: Int!, $ts_end: Int!, $last_id: String) {
      swaps(first: 1000, where: {timestamp_gte: $ts_start, timestamp_lte: $ts_end, id_gt: $last_id}) {
        id
        pool {
          id
        }
        sender
        timestamp
        amountUSD
      }
    }
    """

    # fetch swaps
    last_id = ""
    swaps = []
    while True:
        variables = {
            "ts_start": int(timestamp_start),
            "ts_end": int(timestamp_end),
            "last_id": last_id,
        }

        result_swaps = requests.post(
            V3_AMM_SUBGRAPH[chain],
            json={"query": swaps_query, "variables": variables},
        )
        data = json.loads(result_swaps.text)

        if len(data["data"]["swaps"]) == 0:
            break

        swaps += data["data"]["swaps"]
        last_id = swaps[-1]["id"]

    return swaps
