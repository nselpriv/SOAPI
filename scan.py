from neo4j import GraphDatabase
from pprint import pprint 
import json
from config import neo4j_config 

uri = neo4j_config["uri"] 
username = neo4j_config["username"] 
password = neo4j_config["password"] 
driver = GraphDatabase.driver(uri, auth=(username, password))


def find_security_nodes(tx, _obj_uid):
    query = """
    MATCH (n {uid: $_obj_uid})-->(m)
    WHERE m.type = 'security'
    RETURN m
    """
    result = tx.run(query, _obj_uid=_obj_uid)
    results = [record for record in result.data()]
    return results

def check_security(tx):
    query = """
    MATCH (n)
    WHERE n.type = 'security'
    RETURN n
    """
    result = tx.run(query)
    results = [record for record in result.data()]
    return results


def find_paths(tx, _obj_uid):
    query = """
    MATCH (start), (end {uid: $_obj_uid})
	WHERE start.uid STARTS WITH "path_"
	MATCH path = (start)-[*..10]->(end)
	RETURN path
    """
    result = tx.run(query, _obj_uid=_obj_uid)
    results = [record for record in result.data()]
    return results

def find_objects(tx):
    query = """
    MATCH (n:Object) RETURN n
    """
    result = tx.run(query)
    results = [record for record in result.data()]
    return results

with driver.session() as session:
    try:
        objects = session.execute_read(find_objects)
        #print(objects)
        paths = set()
        for _object in objects:
            connections = session.execute_read(find_paths, _object["n"]["uid"])
            protected = False
            public_access = False
            for connection in connections:
                path = ""
                verb = ""
                for p in connection["path"]:
                    if type(p) is dict:
                        if p["type"] == "path":
                            path = p["name"]
                        if p["type"] == "verb":
                            verb = p["name"]
                            # todo: check if security is optional
                            security_objects = session.execute_read(find_security_nodes, p["uid"])
                            if len(security_objects) > 0:
                                protected = True
                            if len(security_objects) == 0:
                                public_access = True
                if protected:
                    pass
                    #print("[Protected] Object " +  _object["n"]["name"]  + "can be reached from " + verb + " " + path)
                else:
                    pass
                    #print("[Public] Object " +  _object["n"]["name"]  + "can be reached from " + verb + " " + path)
            if protected and public_access:
                print("[+++++] Object " +  _object["n"]["name"] + " can be reached from public & protected endpoints")
            #print("------")
    except:
        print("[!] Error in querying the Neo4j DB")


    print("==== SECOND CHECK ====")
    try:
        sec_objects = session.execute_read(check_security)
        if len(sec_objects) > 0:
            objects = session.execute_read(find_objects)
            paths = set()
            for _object in objects:
                connections = session.execute_read(find_paths, _object["n"]["uid"])
                protected = False
                public_access = False
                for connection in connections:
                    path = ""
                    verb = ""
                    for p in connection["path"]:
                        if type(p) is dict:
                            if p["type"] == "path":
                                path = p["name"]
                            if p["type"] == "verb":
                                verb = p["name"]
                                # todo: check if security is optional
                                security_objects = session.execute_read(find_security_nodes, p["uid"])
                                if len(security_objects) == 0:
                                    if verb == "get":
                                        print("[Public Read] Object " +  _object["n"]["name"]  + " can be reached from " + verb + " " + path)
                                    else:
                                        print("[Public Modify] Object " +  _object["n"]["name"]  + " can be reached from " + verb + " " + path)
    except:
        print("Error checking if security exists")