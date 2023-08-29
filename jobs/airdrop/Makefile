-include .env

build:
	docker build -t sushi-operations-airdrop-job .

run-image:
	docker run --env-file .env -it --rm sushi-operations-airdrop-job --network core --token 0x40375C92d9FAf44d2f9db9Bd9ba41a3317a2404f --amount 22

run:
	python src/main.py --network core --token 0x40375C92d9FAf44d2f9db9Bd9ba41a3317a2404f --amount 50