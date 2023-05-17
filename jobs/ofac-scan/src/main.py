import re
import json
import requests

# Download the text file
response = requests.get('https://www.treasury.gov/ofac/downloads/sdnlist.txt')
data = response.text

# Use a regular expression to find all Ethereum addresses
ethereum_addresses = re.findall(r'ETH 0x[a-fA-F0-9]{40}', data)
ethereum_addresses = [address[4:]
                      for address in ethereum_addresses]  # Remove 'ETH ' prefix

# Repeat for Binance Smart Chain addresses
bsc_addresses = re.findall(r'BSC 0x[a-fA-F0-9]{40}', data)
bsc_addresses = [address[4:]
                 for address in bsc_addresses]  # Remove 'BSC ' prefix

# Store both lists in a dictionary
addresses = {
    'ethereum': ethereum_addresses,
    'bsc': bsc_addresses,
}

# Write the addresses to a JSON file
with open('./data/ofac-addresses.json', 'w') as file:
    json.dump(addresses, file)
