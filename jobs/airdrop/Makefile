-include .env

build:
	docker build -t sushi-operations-airdrop-job .

run-image:
	docker run --env-file .env -it --rm sushi-operations-airdrop-job --network thundercore --token 0xabd380327fe66724ffda91a87c772fb8d00be488 --amount 24

run:
	python src/main.py --network thundercore --token 0xabd380327fe66724ffda91a87c772fb8d00be488 --amount 24