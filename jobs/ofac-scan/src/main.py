import re
import json
import requests
import time
from github import Github
from os import environ

SDN_URL = "https://www.treasury.gov/ofac/downloads/sdnlist.txt"
REPO_NAME = "sushiswap/sushi-operations"
ETH_FILE_PATH = "jobs/ofac-scan/data/ofac-addresses.txt"

# Get the SDN list
response = requests.get(SDN_URL)
sdn_list = response.text

# Parse the ETH addresses
ethereum_addresses = re.findall("ETH 0x[a-fA-F0-9]{40}", sdn_list)
bsc_addresses = re.findall("BSC 0x[a-fA-F0-9]{40}", sdn_list)
new_addresses = {
    "ethereum": ethereum_addresses,
    "bsc": bsc_addresses
}

# Create a Github instance
g = Github(environ.get('GITHUB_TOKEN'))
repo = g.get_repo(REPO_NAME)

# Get the current addresses from the GitHub file
contents = repo.get_contents(ETH_FILE_PATH)
current_addresses = json.loads(contents.decoded_content)

# Check if there are any new addresses
if current_addresses != new_addresses:
    # Create a new branch
    branch = repo.get_branch("main")
    repo.create_git_ref(ref=f"refs/heads/new_addresses", sha=branch.commit.sha)

    # Update the file with the new addresses
    repo.update_file(contents.path, "Update addresses", json.dumps(
        new_addresses, indent=2), contents.sha, branch="new_addresses")

    # Create a pull request
    repo.create_pull(
        title="New addresses added",
        body="Updated the list of addresses from the SDN list.",
        head="new_addresses",
        base="main"
    )
