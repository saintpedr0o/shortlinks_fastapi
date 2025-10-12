up:
	docker compose -f docker-compose.yaml --env-file .env up

build:
	docker compose -f docker-compose.yaml --env-file .env up --build

delete:
	docker compose -f docker-compose.yaml down

delete_volume:
	docker compose -f docker-compose.yaml down -v
	
test:
	docker compose -f docker-compose.test.yaml --env-file .env.test up --build --abort-on-container-exit; docker compose -f docker-compose.test.yaml down -v
