run: stop
	docker compose up -d
stop:
	docker compose down
build:
	poetry export -f requirements.txt --without-hashes --output requirements.txt
	mv requirements.txt transaction_service/
	docker compose build
	rm transaction_service/requirements.txt