import argparse
import requests
import json
from web3 import Web3, HTTPProvider


MAINNET_RPC_URL = 'https://eth.llamarpc.com'

MASTERCHEFV1_ENDPOINT = 'https://api.thegraph.com/subgraphs/name/sushiswap/master-chef'
MASTERCHEFV2_ENDPOINT = 'https://api.thegraph.com/subgraphs/name/sushiswap/master-chefv2'


def main():

    print(f'Pulling data from chef graph endpoint...')

    pools_query = """query {
      pools(first: 1000) {
        id
        users (first: 1000, where: {amount_gte: 0} orderBy: amount, orderDirection: desc) {
          address
        }
      }
    }
    """

    result = requests.post(
        MASTERCHEFV1_ENDPOINT, json={'query': pools_query})
    data = json.loads(result.text)
    pools = data['data']['pools']

    pool_user_counts = {}
    for pool in pools:
        pool_user_counts[pool['id']] = len(pool['users'])
    print(pool_user_counts)


if __name__ == '__main__':
    main()
