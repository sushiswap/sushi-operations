import json

user_data_file_path = "./data/output/arbitrum-token-claims.json"

# Load user data
with open(user_data_file_path, 'r') as file:
    user_data = json.load(file)

user_count = {}

# Count occurrences of each user
for entry in user_data:
    user = entry['user']
    if user in user_count:
        user_count[user] += 1
    else:
        user_count[user] = 1

# Find and print duplicates
duplicates_found = False
for user, count in user_count.items():
    if count > 1:
        duplicates_found = True
        print(f'Duplicate user: {user}, count: {count}')

if not duplicates_found:
    print('No duplicate users found.')
