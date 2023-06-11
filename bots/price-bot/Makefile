-include .env

build:
	docker build -t sushi-operations-price-bot .

run-image:
	docker run --env-file .env -it --rm sushi-operations-price-bot

run:
	python src/main.py