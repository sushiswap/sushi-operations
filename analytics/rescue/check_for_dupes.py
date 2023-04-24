import json

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
    pre_tree_inputs = './data/pre-tree-inputs/' + network + '-token-claims.json'

    # Load user data
    with open(pre_tree_inputs, 'r') as file:
        user_data = json.load(file)

    user_token_count = {}

    # Count occurrences of each user
    for entry in user_data:
        user = entry['user']
        token = entry['token']
        if (user, token) in user_token_count:
            user_token_count[(user, token)] += 1
        else:
            user_token_count[(user, token)] = 1

    # Find and print duplicates
    duplicates_found = False
    for (user, token), count in user_token_count.items():
        if count > 1:
            duplicates_found = True
            print(
                f'Duplicate user-token pair: User: {user}, Token: {token}, count: {count}')

    if not duplicates_found:
        print('No duplicate users found.')
