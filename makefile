.PHONY: setup, run, fast, clean-docker

run:
	docker compose up -d

clean:
	docker rmi -f soapi-soapi:latest neo4j:2025.02.0-community-bullseye

clean-2:
    docker compose down --volumes