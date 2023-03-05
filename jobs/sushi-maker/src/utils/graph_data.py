import requests
import json

EXCHANGE_GRAPH_ENDPOINTS = {
    "mainnet": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-ethereum",
    "arbitrum": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-arbitrum-backup"
}


def fetch_lp_tokens(address, chain):
    user_lp_query = """query($addy: String!, $last_id: String) {
    user(id: $addy) {
      liquidityPositions(first: 1000, where: { id_gt: $last_id }) {
        id
        pair {
          id
          token0Price
          token1Price
          name
          reserve0
          reserve1
          totalSupply
          reserveUSD
          trackedReserveETH
          token0 {
            id
            name
            symbol
            decimals
          }
          token1 {
            id
            name
            symbol
            decimals
          }
        }
        liquidityTokenBalance
        }
      }
    }
    """

    last_id = ""
    user_lp_tokens = []
    while (True):

        variables = {"addy": address.lower(), "last_id": last_id}
        result = requests.post(
            EXCHANGE_GRAPH_ENDPOINTS[chain], json={
                "query": user_lp_query, "variables": variables}
        )
        data = json.loads(result.text)

        if len(data['data']['user']['liquidityPositions']) == 0:
            break

        user_lp_tokens += data['data']['user']['liquidityPositions']
        last_id = user_lp_tokens[-1]['id']

    sorted_lp_tokens = sorted(
        user_lp_tokens,
        key=lambda d: 0 if float(d['pair']['totalSupply']) == 0 else (float(d['pair']['reserveUSD']) * (
            float(d['liquidityTokenBalance']) / float(d['pair']['totalSupply']))),
        reverse=True
    )

    return sorted_lp_tokens
