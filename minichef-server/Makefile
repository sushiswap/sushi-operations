-include .env

build:
	docker build -t sushi-operations-minichef-server-job .

run-image:
	docker run --env-file .env -it --rm sushi-operations-minichef-server-job

run:
	python main.py