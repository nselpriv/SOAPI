.PHONY: setup, run, fast, clean-docker

setup:
	docker compose up -d 

run: setup
	docker exec -it SOAPI bash

fast: 
	docker compose run soapi bash

clean:
	docker rmi -f soapi-soapi:latest neo4j:2025.02.0-community-bullseye