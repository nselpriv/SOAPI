import os
import re
import time
import requests
from neo4j import GraphDatabase

from config import BUG_BOUNTY_USERNAME
from scan import find_unauthenticated_endpoints

def find_unauthenticated_endpoints(tx):
    query = """
        MATCH (v {type: "verb"})<-[]-(incoming)
        WHERE NOT EXISTS {
            MATCH (v)-[]->(s {type: "security"})
        }
        RETURN v, incoming
    """
    result = tx.run(query)
    results = [record for record in result.data()]
    return results

# Set up the connection details
uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
username = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "mysecurepassword")
driver = GraphDatabase.driver(uri, auth=(username, password))

# Revised query that retrieves the full chain including parameter nodes via `has param`
query = """
MATCH (p:Path)-[r:can]-(v)
// WHERE v.name in ['get'] //AND NOT (v)-[:`secured by`]->()
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
    """
    Replace placeholders like {orderId} in the URL with corresponding values from params.
    """
    placeholders = re.findall(r'\{(\w+)\}', url)
    for key in placeholders:
        if key in params:
            url = url.replace(f'{{{key}}}', str(params[key]))
    return url

def prompt_for_parameters(default_params):
    """
    Iterate through the possible parameters and
    prompt the user to enter a new value or press Enter to use the default.
    The user can also type 'next' to skip this record.
    Returns a dictionary with updated parameters or None if the user decides to skip.
    """
    new_params = {}
    print("\nProvide new values for parameters (or press Enter to use the default):")
    # Process each key
    for key, default in default_params.items():
        user_val = input(f"   {key} (default: {default}): ").strip()
        if user_val.lower() == "next":
            print("Skipping this record.")
            return None  # Signal to skip
        # If input is blank, use the default value
        if user_val == "":
            new_params[key] = default
        else:
            new_params[key] = user_val
    # If no parameters were defined, note that an empty parameter set is being used.
    if not new_params:
        print("No parameters to enter; using an empty parameter set.")
    return new_params

def interactive_process_results(results, base_url):
    """
    For each record, print out details, then iterate through the parameters
    and ask for user input. If the user does not supply a value, the default is used.
    Typing 'next' at any prompt will skip the current record.
    """
    for idx, record in enumerate(results, start=1):
        p = record.get("p")
        v = record.get("v")
        if not p or not v:
            print("Record missing required data. Skipping record.")
            continue

        # Build the default parameters dictionary from descendantParams.
        default_params = {}
        descendantParams = record.get("descendantParams")
        if descendantParams:
            for param_node in descendantParams:
                pname = param_node.get("name")
                if pname:
                    # If the parameter is in the format 'string <key>', split to get the key.
                    if pname.startswith("string "):
                        key = pname.split(" ", 1)[1]
                    else:
                        key = pname
                    # If key is 'tenant', default it to "uk", otherwise default to "1"
                    if key == "tenant":
                        default_params[key] = "uk"
                    else:
                        default_params[key] = "1"
        # Determine endpoint and method.
        endpoint_template = p.get("name")
        method = v.get("name").lower()  # expecting 'post', 'get', etc.
        # Build the URL using default parameters first.
        filled_endpoint = replace_placeholders_in_url(endpoint_template, default_params)
        url = base_url.rstrip("/") + "/" + filled_endpoint.lstrip("/")

        print("\n------------------------------------------------")
        print(f"Record #{idx}")
        print("HTTP Method:", method.upper())
        print("URL (using default parameter substitution):", url)
        print("Default Parameters:", default_params)

        # Interactive loop for this record.
        while True:
            choice = input("\nPress Enter to use default parameters & send a request, type 'edit' to modify parameters, or 'next' to skip this record: ").strip().lower()
            if choice == "next":
                print("Skipping to the next record.")
                break

            if choice == "edit":
                updated_params = prompt_for_parameters(default_params)
                if updated_params is None:
                    # User requested skip during parameter entry.
                    break
            else:
                updated_params = default_params.copy()

            # Replace placeholders in the original endpoint template using the chosen parameters.
            current_filled_endpoint = replace_placeholders_in_url(endpoint_template, updated_params)
            current_url = base_url.rstrip("/") + "/" + current_filled_endpoint.lstrip("/")

            print(f"\nMaking {method.upper()} request to:")
            print(f"  {current_url}")
            print(f"with parameters: {updated_params}")

            # Optional delay if needed
            time.sleep(2)

            headers = {"x-bug-bounty": BUG_BOUNTY_USERNAME}
            try:
                if method == "post":
                    response = requests.post(current_url, json=updated_params, headers=headers)
                elif method == "put":
                    response = requests.put(current_url, json=updated_params, headers=headers)
                elif method == "delete":
                    response = requests.delete(current_url, json=updated_params, headers=headers)
                else:
                    response = requests.get(current_url, params=updated_params, headers=headers)

                print(f"\nStatus Code: {response.status_code}")
                print("Response:")
                print(response.text)
            except Exception as e:
                print(f"HTTP request failed: {e}")

            reattempt = input("\nPress Enter to try with different parameter values, or type 'next' (or 'n') to move to the next record: ").strip().lower()
            if reattempt in ("next", "n"):
                break

if __name__ == "__main__":
    base_url = "https://uk.api.just-eat.io/"
    with driver.session() as session:
        results = session.execute_read(run_query, query)
        # You could also use a different query such as find_unauthenticated_endpoints(session)
        interactive_process_results(results, base_url)
    driver.close()