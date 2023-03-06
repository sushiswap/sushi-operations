import requests
import json

from utils.config import CHAIN_MAP

TOKEN_LIST_URL = "https://token-list.sushi.com/"


def fetch_whitelisted_tokens(chain):
    result = requests.get(TOKEN_LIST_URL)
    data = json.loads(result.text)
    tokens = data['tokens']
    # filter by chain and keep only the address
    chain_tokens = [
        token['address'].lower() for token in tokens if token['chainId'] == CHAIN_MAP[chain]]

    return chain_tokens
