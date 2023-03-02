import requests
import json

EXCHANGE_GRAPH_ENDPOINTS = {
    "arbitrum": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange-arbitrum-backup"
}


def fetch_lp_tokens(address, chain):
    user_lp_query = """query($addy: String!) {
    user(id: "0xa19b3b22f29e23e4c04678c94cfc3e8f202137d8") {
      liquidityPositions(first: 1000, orderBy: liquidityTokenBalance, orderDirection: desc) {
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
          }
          token1 {
            id
          }
        }
        liquidityTokenBalance
        }
      }
    }
    """

    variables = {"addy": address}
    result = requests.post(
        EXCHANGE_GRAPH_ENDPOINTS[chain], json={
            "query": user_lp_query, "variables": variables}
    )
    data = json.loads(result.text)
    user_lp_tokens = data['data']['user']['liquidityPositions']

    sorted_lp_tokens = sorted(
        user_lp_tokens,
        key=lambda d: float(d['pair']['reserveUSD']) * (
            float(d['liquidityTokenBalance']) / float(d['pair']['totalSupply'])),
        reverse=True
    )

    return sorted_lp_tokens
