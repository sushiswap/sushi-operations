import requests
import json

from utils.config import (
    CLASSIC_AMM_SUBGRAPH,
    TRIDENT_AMM_SUBGRAPH,
    V3_AMM_SUBGRAPH,
    ROUTE_PROCESSOR_SUBGRAPH,
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

def fetch_mint_data_v3(network, timestamp_start, timestamp_end):
    mints_query = """query($ts_start: Int!, $ts_end: Int!, $last_id: String) {
        mints(first: 1000, where: {timestamp_gte: $ts_start, timestamp_lte: $ts_end, id_gt: $last_id}) {
            id
            pool {
                id
            }
            origin
            timestamp
            amountUSD
        }
    }
    """

    # fetch mints
    last_id = ""
    mints = []
    while True:
        variables = {
            "ts_start": int(timestamp_start),
            "ts_end": int(timestamp_end),
            "last_id": last_id,
        }

        result_mints = requests.post(
            V3_AMM_SUBGRAPH[network],
            json={"query": mints_query, "variables": variables},
        )
        data = json.loads(result_mints.text)

        if len(data["data"]["mints"]) == 0:
            break

        mints += data["data"]["mints"]
        last_id = mints[-1]["id"]

    return mints

def fetch_routes(network, timestamp_start, timestamp_end):
    routes_query = """query($ts_start: Int!, $ts_end: Int!, $last_id: String) {
        routes(first: 1000, where: {timestamp_gte: $ts_start, timestamp_lte: $ts_end, id_gt: $last_id}) {
            id
            from
            to
            tokenIn
            tokenOut
            amountIn
            amountOut
            timestamp
        }
    }
    """
    
    # fetch routes
    last_id = ""
    routes = []
    while True:
        variables = {
            "ts_start": int(timestamp_start),
            "ts_end": int(timestamp_end),
            "last_id": last_id,
        }

        result_routes = requests.post(
            ROUTE_PROCESSOR_SUBGRAPH[network],
            json={"query": routes_query, "variables": variables},
        )
        data = json.loads(result_routes.text)

        if len(data["data"]["routes"]) == 0:
            break

        routes += data["data"]["routes"]
        last_id = routes[-1]["id"]

    return routes

def fetch_v3_current_prices(network, tokens):
    token_price_query = """query($tokens: [String!]!) {
        tokens(where: {id_in: $tokens}) {
            id
            decimals
            derivedETH
        }
        bundle(id: "1") {
            ethPriceUSD
        }
    }
    """

    variables = {
        "tokens": tokens,
    }
    result = requests.post(
        V3_AMM_SUBGRAPH[network],
        json={"query": token_price_query, "variables": variables},
    )
    data = json.loads(result.text)

    token_prices = {key: {} for key in tokens}
    for token in data["data"]["tokens"]:
        token_prices[token["id"]]['usdPrice'] = float(token["derivedETH"]) * float(data["data"]["bundle"]["ethPriceUSD"])
        token_prices[token["id"]]['decimals'] = token["decimals"]

    return token_prices