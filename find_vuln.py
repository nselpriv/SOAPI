import os
import re
import requests
from neo4j import GraphDatabase

# Set up the connection details
uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
username = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "mysecurepassword")
driver = GraphDatabase.driver(uri, auth=(username, password))

# Revised query that retrieves the full chain including parameter nodes via `has param`
query = """
MATCH (p:Path)-[r:can]-(v)
WHERE v.name in ['get'] //AND NOT (v)-[:`secured by`]->()
OPTIONAL MATCH path = (v)-[rels:contains*]->(descendant)
OPTIONAL MATCH (descendant)-[:`has param`*1..]->(param)
RETURN p, r, v,
       nodes(path)         AS connectedNodes,
       relationships(path) AS connectedRels,
       collect(DISTINCT param) AS descendantParams
LIMIT 100000
"""

def run_query(tx, query):
    result = tx.run(query)
    return [record.data() for record in result]

def replace_placeholders_in_url(url, params):
    """Replace placeholders like {orderId} in the URL with corresponding values from params."""
    placeholders = re.findall(r'\{(\w+)\}', url)
    for key in placeholders:
        if key in params:
            url = url.replace(f'{{{key}}}', str(params[key]))
    return url

def make_http_request(record, base_url):
    p = record.get("p")
    v = record.get("v")

    if not p or not v:
        raise ValueError("Record must contain p and v nodes.")

    # Extract endpoint and method
    endpoint = p.get("name")
    method = v.get("name").lower()  # expecting 'post', 'get', etc.

    # Prepare the parameters dictionary.
    params = {}
    descendantParams = record.get("descendantParams")
    if descendantParams:
        for param_node in descendantParams:
            pname = param_node.get("name")
            if pname and pname.startswith("string "):
                key = pname.split(" ", 1)[1]
                params[key] = "1"
            else:
                key = pname if pname else None
                if key:
                    params[key] = "1"

    # Replace placeholders in endpoint with actual param values
    endpoint = replace_placeholders_in_url(endpoint, params)

    # Build the full URL
    url = base_url.rstrip("/") + "/" + endpoint.lstrip("/")

    # Make the HTTP request using the correct method type
    try:
        if method == "post":
            response = requests.post(url, json=params)
        elif method == "put":
            response = requests.put(url, json=params)
        elif method == "delete":
            response = requests.delete(url, json=params)
        else:
            response = requests.get(url, params=params)

        print(f"\nRequest: {method.upper()} {url}")
        print(f"Params: {params}")
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.text)

        return response
    except Exception as e:
        print(f"HTTP request failed: {e}")
        return None

def process_results(results, base_url):
    for record in results:
        try:
            make_http_request(record, base_url)
        except Exception as e:
            print(f"Error processing record {record}: {e}")

if __name__ == "__main__":
    base_url = "https://uk-partnerapi.just-eat.io/"

    with driver.session() as session:
        results = session.execute_read(run_query, query)
        process_results(results, base_url)
    driver.close()
