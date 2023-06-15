# Airdrop Tokens to Wallets

## To Build

Create a `data` directory under `src`, and add a `wallet-list.txt` file with wallet addresses for each line.

Copy `.env.sample` to `.env` and fill in the environment variables.

Then run: 

`make build`


## To Run

Update the Makefile `run-image` command, and change the network, address of the token you want to airdrop and the amount at the end.

Then run:

`make run-image`