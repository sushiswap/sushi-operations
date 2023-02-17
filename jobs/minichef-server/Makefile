-include .env

build:
	docker build -t sushi-operations-minichef-server-job .

run-image:
	docker run --env-file .env -it --rm sushi-operations-minichef-server-job

run-image-ignore-gas:
	docker run --env-file .env -it --rm sushi-operations-minichef-server-job --ignoreGas

run-image-priority:
	docker run --env-file .env -it --rm sushi-operations-minichef-server-job --priority

run:
	python main.py