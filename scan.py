from neo4j import GraphDatabase
from pprint import pprint 
import json
from config import neo4j_config 

uri = neo4j_config["uri"] 
username = neo4j_config["username"] 
password = neo4j_config["password"] 
driver = GraphDatabase.driver(uri, auth=(username, password))



def get_paths_with_response(tx, _leaf_name):
    query = """
        MATCH p = (start {type: "path"})-[*]->(mid {type: "responses"})-[*]->(end {name: $_leaf_name})
        RETURN p
    """
    result = tx.run(query, _leaf_name=_leaf_name)
    results = [record for record in result.data()]
    return results

def get_parameters(tx, _verb_uid):
    query = """
        MATCH p=(startNode {uid: $_verb_uid})-[*]->(connectedNode)
        WHERE NONE(n IN nodes(p) WHERE n.type IN ['responses', 'security']) 
        WITH last(nodes(p)) AS leafNode
        WHERE NOT (leafNode)-[]->()
        RETURN leafNode
    """
    result = tx.run(query, _verb_uid=_verb_uid)
    results = [record for record in result.data()]
    return results

# returns public readble fields below a given node
def get_read_fields(tx, _obj_uid):
    query = """ 
        MATCH p=(startNode {uid: $_obj_uid})-[*]->(connectedNode)
        WHERE NONE(n IN nodes(p) WHERE n.type IN ['parameters', 'security', 'body']) 
        WITH last(nodes(p)) AS leafNode
        WHERE NOT (leafNode)-[]->()
        RETURN leafNode
    """
    result = tx.run(query, _obj_uid=_obj_uid)
    results = [record for record in result.data()]
    return results

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

def find_authenticated_endpoints(tx):
    query = """
    MATCH (v {type: "verb"})<-[]-(incoming) 
    WHERE EXISTS {
        MATCH (v)-[]->(s {type: "security"})
    }
    RETURN v, incoming
    """
    result = tx.run(query)
    results = [record for record in result.data()]
    return results

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

def find_verb_objects(tx):
    query = """
    MATCH (n)
    WHERE n.type = "verb"
    RETURN n
    """
    result = tx.run(query)
    results = [record for record in result.data()]
    return results



with driver.session() as session:
    print("")
    print("[+] Stats:")
    print("")
    
    objects = session.execute_read(find_verb_objects)
    print("There are " + str(len(objects)) + " unique endpoints" )
    public_endpoints = session.execute_read(find_unauthenticated_endpoints)
    print(" - " + str(len(public_endpoints)) + " public endpoints" )
    protected_endpoints = session.execute_read(find_authenticated_endpoints)
    print(" - " + str(len(protected_endpoints)) + " protected endpoints" )


#might be worth considering to search only by parameter name in the responses, instead of including also the parameter type
# i.e: "username" instead of "string username"

with driver.session() as session:
    print("")
    print("[+] IDOR ID Finder:")
    print("")

    verbs = session.execute_read(find_verb_objects)
    for verb in verbs:
        parameters = session.execute_read(get_parameters, verb['n']['uid'])
        if parameters is not None:
            for parameter in parameters:
                connections = session.execute_read(get_paths_with_response, parameter['leafNode']['name'])
                if connections is not None:
                    print("")
                    print("[*] " + verb['n']['uid'])
                    print(parameter['leafNode']['name'])
                    for connection in connections:
                        path_name = ""
                        verb_name = ""
                        for p in connection["p"]:
                            if type(p) is dict:
                                if p["type"] == "path":
                                    path_name = p["name"]
                                if p["type"] == "verb":
                                    verb_name = p["name"]
                        print(" -> " + verb_name + " " + path_name)

            print("")



with driver.session() as session:
    print(" ")
    print("[+] List objects accessible through public & private endpoints")
    print(" ")
    public_endpoints = session.execute_read(find_unauthenticated_endpoints)
    protected_endpoints = session.execute_read(find_authenticated_endpoints)
    objects = session.execute_read(find_objects)
    public = []
    protected = []
    
    try:
        #print("[+] Public endpoints")
        for endpoint in public_endpoints:
            #print(endpoint['v']['name'] + " " + endpoint['incoming']['name'])
            public.append(endpoint['v']['name'] + " " + endpoint['incoming']['name'])
        #print("[+] Protected endpoints")
        for endpoint in protected_endpoints:
            #print(endpoint['v']['name'] + " " + endpoint['incoming']['name'])
            protected.append(endpoint['v']['name'] + " " + endpoint['incoming']['name'])
        for _object in objects:
            access = []
            connections = session.execute_read(find_paths, _object["n"]["uid"])
            for connection in connections:
                path = ""
                verb = ""
                for p in connection["path"]:
                    if type(p) is dict:
                        if p["type"] == "path":
                            path = p["name"]
                        if p["type"] == "verb":
                            verb = p["name"]
                access.append(verb + " " + path)
            #print(access)
            public_acc = []
            protected_acc = []
            for acc in access:
                if acc in public:
                    public_acc.append(acc)
                if acc in protected:
                    protected_acc.append(acc)
            if len(public_acc) > 0 and len(protected_acc) > 0:
                print(" ")
                print("[+] " + _object["n"]["name"])
                [print("Public: " + item) for item in public_acc]
                [print("Protected: " +item) for item in protected_acc]

    except:
        print("[!] Error listing objects accessible through public & private endpoints!")


    #### List public endpoints ####
    print("")
    print("[+] List public endpoints")
    print("")
    try:
        objects = session.execute_read(find_unauthenticated_endpoints)
        for _object in objects:
            print(_object['v']['name'] + " " + _object['incoming']['name'])
    except:
        print("[!] Error to list public endpoints")


    #### List public fields ####
    print("")
    print("[+] List public readble fields")
    print("")
    
    objects = session.execute_read(find_unauthenticated_endpoints)
    for _object in objects:
        paths = session.execute_read(get_read_fields, _object['v']['uid'])
        print("----")
        print(_object['v']['name'].upper() + " " + _object['incoming']['name'])
        for path in paths:
            print("[-] " + path['leafNode']['name'])


    print("")
    print("[+] IDOR Finder")
    print("")

