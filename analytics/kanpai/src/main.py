import argparse
import requests
import json
from datetime import datetime, timedelta

EXCHANGE_ENDPOINTS = {
    "mainnet": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange",
    "arbitrum": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-arbitrum-backup",
}

MAKER_ADDRESS = {
    "mainnet": "0x5ad6211cd3fde39a9cecb5df6f380b8263d1e277",
    "arbitrum": "0xa19b3b22f29e23e4c04678c94cfc3e8f202137d8",
}

WETH_ADDRESS = {
    "mainnet": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "arbitrum": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
}


def main():
    print("Pulling data from exchange graph endpoint...")

    maker_burns_query = """query($maker: String!, $ts: Int!) {
    burns(first: 1000, where: {sender: $maker, timestamp_gte: $ts}) {
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

    maker_swaps_query = """query($maker: String!, $ts: Int!) {
      swaps(first: 1000, where: {sender: $maker, timestamp_gte: $ts}) {
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

    month_before_ts = datetime.now() - timedelta(85)

    total_weth_earned = 0
    for network in EXCHANGE_ENDPOINTS:
        variables = {"maker": MAKER_ADDRESS[network], "ts": int(
            month_before_ts.timestamp())}
        result_burns = requests.post(
            EXCHANGE_ENDPOINTS[network], json={'query': maker_burns_query, 'variables': variables})
        result_swaps = requests.post(
            EXCHANGE_ENDPOINTS[network], json={'query': maker_swaps_query, 'variables': variables})

        data_burns = json.loads(result_burns.text)
        data_swaps = json.loads(result_swaps.text)
        burns = data_burns['data']['burns']
        swaps = data_swaps['data']['swaps']

        weth_burned = 0
        print(f"There are {len(burns)} burns...")
        for burn in burns:
            if burn['pair']['token0']['id'] == WETH_ADDRESS[network]:
                weth_burned += float(burn['amount0'])
            elif burn['pair']['token1']['id'] == WETH_ADDRESS[network]:
                weth_burned += float(burn['amount1'])

        print(
            f"Maker burned {weth_burned} WETH in the last 30 days on {network}")
        total_weth_earned += weth_burned

        weth_swapped = 0
        print(f"There are {len(swaps)} swaps...")
        for swap in swaps:
            if (swap['pair']['token0']['id'] == WETH_ADDRESS[network]) and (float(swap['amount0Out']) > 0):
                weth_swapped += float(swap['amount0Out'])
            elif (swap['pair']['token1']['id'] == WETH_ADDRESS[network]) and (float(swap['amount1Out']) > 0):
                weth_swapped += float(swap['amount1Out'])

        print(
            f"Maker swapped for {weth_swapped} WETH in the last 30 days on {network}")
        total_weth_earned += weth_swapped

    print(f"Treasury earned {total_weth_earned} WETH in the last 30 days")


if __name__ == '__main__':
    main()
