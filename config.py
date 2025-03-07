import os

neo4j_config = {
    "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),  # Use env var, fallback for local dev
    "username": os.getenv("NEO4J_USER", "neo4j"),
    "password": os.getenv("NEO4J_PASSWORD", "mysecurepassword")
}