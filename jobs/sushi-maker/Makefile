-include .env

build:
	docker build -t sushi-operations-weth-maker-job .

run-burn-arbitrum:
	docker run --env-file .env -it --rm sushi-operations-weth-maker-job --chain arbitrum --burn

run-unwind-arbitrum:
	docker run --env-file .env -it --rm sushi-operations-weth-maker-job --chain arbitrum --unwind

run:
	python src/main.py