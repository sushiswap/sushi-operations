import csv
from collections import defaultdict

file_path = './data/manual-claims.csv'

totals = defaultdict(lambda: defaultdict(float))

with open(file_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        chain = row['Chain']
        token_name = row['TokenName']
        notes = row['Notes']
        amount = float(row['Amount'].replace(',', ''))

        if 'TRUE' in row['Sent']:
            continue

        if 'stable' in notes:
            if chain == 'bsc':
                token_name = 'USDT'
            else:
                token_name = 'USDC'
            amount = float(row['$$ Value'].replace(',', ''))

        totals[chain][token_name] += amount

for chain, tokens in totals.items():
    print(f'Chain: {chain}')
    for token, total in tokens.items():
        print(f'  Token: {token}, Total: {total}')
    print()
