import json
from collections import defaultdict


def hex_to_int(hex_string):
    return int(hex_string, 16)


networks = [
    'arbitrum',
    'avalanche',
    'boba',
    'bsc',
    'ethereum',
    'fantom',
    'nova',
    'optimism',
    'polygon',
]

for network in networks:
    print(network)
    pre_tree_inputs = './data/output/' + network + '-token-claims.json'
    tree_file = './data/trees/' + network + '-tree.json'

    # Load user data
    with open(pre_tree_inputs, 'r') as file:
        user_data = json.load(file)

    # Load tree data
    with open(tree_file, 'r') as file:
        tree_data = json.load(file)

    output_totals = defaultdict(int)
    tree_totals = defaultdict(int)

    # Calculate output_totals
    for entry in user_data:
        user = entry['user']
        token = entry['token']
        value = int(entry['value'])
        output_totals[(user, token)] += value

    # Calculate tree_totals
    for claim in tree_data['claims']:
        user = claim['user']
        token = claim['token']
        value = hex_to_int(claim['amount']['hex'])
        tree_totals[(user, token)] += value

    # Compare output_totals and tree_totals
    everything_matches = True
    for user_token, output_total in output_totals.items():
        tree_total = tree_totals[user_token]
        if output_total != tree_total:
            everything_matches = False
            print(
                f"Mismatch for User: {user_token[0]}, Token: {user_token[1]} - Output total: {output_total}, Tree total: {tree_total}")

    if everything_matches:
        print("All totals match.")
