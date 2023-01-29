-include .env

build:
	docker build -t sushi-operations-minichef-server-job-test .

image-run:
	docker run --env-file .env -it --rm sushi-operations-minichef-server-job-test

run:
	python main.py