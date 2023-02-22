import argparse
import requests
import json
from datetime import date, timedelta

EXCHANGE_ENDPOINTS = {
    "mainnet": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange",
    "arbitrum": "",
}


def main():
    print("Pulling data from exchange graph endpoint...")

    maker_burns_query = """query {
    burns(first: 1000, where: {sender: "0x5ad6211cd3fde39a9cecb5df6f380b8263d1e277"}) {
      id
      timestamp
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

    # current_date = date.today()
    # month_before_date = (current_date - timedelta(days=30)).timestamp()

    print(month_before_date)

    result = requests.post(
        EXCHANGE_ENDPOINTS["mainnet"], json={'query': maker_burns_query})
    data = json.loads(result.text)
    burns = data['data']['burns']

    print(burns)


if __name__ == '__main__':
    main()
