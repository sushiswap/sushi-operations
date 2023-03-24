-include .env

build:
	docker build -t sushi-operations-kanpai-bot .

run-image:
	docker run --env-file .env -it --rm sushi-operations-kanpai-bot

run:
	python src/main.py