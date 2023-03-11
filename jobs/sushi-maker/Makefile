-include .env

build:
	docker build -t sushi-operations-weth-maker-job .

run-burn-arbitrum:
	docker run --env-file .env -it --rm sushi-operations-weth-maker-job --chain arbitrum --burn

run-arbitrum:
	docker run --env-file .env -it --rm sushi-operations-weth-maker-job --chain arbitrum --full

run-mainnet:
	docker run --env-file .env -it --rm sushi-operations-weth-maker-job --chain mainnet --full

run-mainnet-read-only:
	docker run --env-file .env -it --rm sushi-operations-weth-maker-job --chain mainnet --full --read

run-polygon:
	docker run --env-file .env -it --rm sushi-operations-weth-maker-job --chain polygon --full


run:
	python src/main.py