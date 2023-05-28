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
    claims_file_path = './data/output/' + network + '-token-claims.json'
    output_file_path = './data/pre-tree-inputs/' + network + '-token-claims.json'

    # Load user data
    with open(claims_file_path, 'r') as file:
        user_data = json.load(file)

    consolidated_data = {}

    # Consolidate duplicate token-user pairs and add their amounts together
    for entry in user_data:
        user = entry['user']
        token = entry['token']
        value = int(entry['value'])
        chain = entry['chain']

        if (token, user) not in consolidated_data:
            consolidated_data[(token, user)] = {
                'token': token, 'user': user, 'chain': chain, 'value': str(value)}
        else:
            consolidated_data[(token, user)]['value'] = str(
                int(consolidated_data[(token, user)]['value']) + value)

    # Write the consolidated data to the output JSON file
    with open(output_file_path, 'w') as file:
        json.dump(list(consolidated_data.values()), file, indent=2)
