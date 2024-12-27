from neo4j_uploader import batch_upload
import json
import re
import os
from config import neo4j_config 

config = {
    "neo4j_uri": neo4j_config["uri"],
    "neo4j_user": neo4j_config["username"],
    "neo4j_password": neo4j_config["password"]
}

data = ""

try:
	with open("neo4j/my_neo4j.json", encoding="utf8") as my_file:
	    data = json.load(my_file)

	result = batch_upload(config, data)
except:
	print("[!] Error uploading data to Neo4j server")