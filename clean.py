from neo4j import GraphDatabase
from pprint import pprint 
import json
from config import neo4j_config 

uri = neo4j_config["uri"] 
username = neo4j_config["username"] 
password = neo4j_config["password"] 

driver = GraphDatabase.driver(uri, auth=(username, password))


def clean(tx):
    query = """
    MATCH (n)
	DETACH DELETE n;
    """
    result = tx.run(query)
    results = [record for record in result.data()]
    return results


try:
	with driver.session() as session:
		results = session.execute_write(clean)
except:
	print("[!] Error deleting the Neo4j DB")
  