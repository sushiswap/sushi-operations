-include .env

build:
	docker build -t sushi-operations-weth-maker-job .

run-image:
	docker run --env-file .env -it --rm sushi-operations-weth-maker-job

run:
	python src/main.py