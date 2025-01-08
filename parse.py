import requests
import json
import re
import os
import sys
from pprint import pp

json_content = ""
directory = 'samples'


## Extract paths + their description + parameters + requestBody + responses 
# print each of them
# create a prompt that asks chatgpt if it does what it says


neo4j_data = {}
neo4j_data["nodes"] = []
neo4j_data["relationships"] = []

# Define Nodes
path_node = {}
verb_node = {}
parameter_node = {}
requestbody_node = {}
response_node = {}
object_node = {}
field_node = {}
security_node = {}

# Define Relationships
object_field_relationship = {}
field_object_relationship = {}
path_verb_relationship = {}
verb_parameter_relationship = {}
verb_requestbody_relationship = {}
verb_response_relationship = {}
requestbody_object_relationship = {}
requestbody_field_relationship = {}
response_object_relationship = {}
response_field_relationship = {}
parameters_relationship = {}
parameters_object_relationship = {}
verb_security_relationship = {}



# Paths
path_node["labels"] = ["Path"]
path_node["key"] = "uid"
path_node["records"] = []

# Verbs
verb_node["labels"] = ["Verb"]
verb_node["key"] = "uid"
verb_node["records"] = []

# Parameters
parameter_node["labels"] = ["Parameter"]
parameter_node["key"] = "uid"
parameter_node["records"] = []

# RequestBody
requestbody_node["labels"] = ["RequestBody"]
requestbody_node["key"] = "uid"
requestbody_node["records"] = []

# Response
response_node["labels"] = ["Response"]
response_node["key"] = "uid"
response_node["records"] = []

# Objects
object_node["labels"] = ["Object"]
object_node["key"] = "uid"
object_node["records"] = []

# Fields
field_node["labels"] = ["Field"]
field_node["key"] = "uid"
field_node["records"] = []

# Security Scheme 
security_node["labels"] = ["Security"]
security_node["key"] = "uid"
security_node["records"] = []

# Add nodes to Neo4J
neo4j_data["nodes"].append(path_node)
neo4j_data["nodes"].append(verb_node)
neo4j_data["nodes"].append(parameter_node)
neo4j_data["nodes"].append(requestbody_node)
neo4j_data["nodes"].append(response_node)
neo4j_data["nodes"].append(object_node)
neo4j_data["nodes"].append(field_node)
neo4j_data["nodes"].append(security_node)

# Add relationships to Neo4J
neo4j_data["relationships"].append(object_field_relationship)
neo4j_data["relationships"].append(field_object_relationship)
neo4j_data["relationships"].append(path_verb_relationship)
neo4j_data["relationships"].append(verb_parameter_relationship)
neo4j_data["relationships"].append(verb_requestbody_relationship)
neo4j_data["relationships"].append(verb_response_relationship)
neo4j_data["relationships"].append(requestbody_object_relationship)
neo4j_data["relationships"].append(response_object_relationship)
neo4j_data["relationships"].append(parameters_relationship)
neo4j_data["relationships"].append(parameters_object_relationship)
neo4j_data["relationships"].append(verb_security_relationship)
neo4j_data["relationships"].append(response_field_relationship)
neo4j_data["relationships"].append(requestbody_field_relationship)






# Object -> Field (object has field)
object_field_relationship["type"] = "has"
object_field_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"Object"}
object_field_relationship["to_node"] = { "record_key":"_to_uid", "node_key":"uid", "node_label": "Field" }
object_field_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
object_field_relationship["records"] = []

# Field -> Object (field is of type object)
field_object_relationship["type"] = "is a"
field_object_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"Field"}
field_object_relationship["to_node"] = { "record_key":"_to_uid", "node_key":"uid", "node_label": "Object" }
field_object_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
field_object_relationship["records"] = []

# Path -> Verb (field is of type object)
path_verb_relationship["type"] = "can"
path_verb_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"Path"}
path_verb_relationship["to_node"] = { "record_key":"_to_uid", "node_key":"uid", "node_label": "Verb" }
path_verb_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
path_verb_relationship["records"] = []

# Verb -> "Parameters", "RequestBody" or "Response"
verb_parameter_relationship["type"] = "contains"
verb_parameter_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"Verb"}
verb_parameter_relationship["to_node"] = {"record_key":"_to_uid", "node_key":"uid", "node_label": "Parameter" }
verb_parameter_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
verb_parameter_relationship["records"] = []

# Verb -> "RequestBody"
verb_requestbody_relationship["type"] = "sends"
verb_requestbody_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"Verb"}
verb_requestbody_relationship["to_node"] = {"record_key":"_to_uid", "node_key":"uid", "node_label": "RequestBody" }
verb_requestbody_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
verb_requestbody_relationship["records"] = []

# Verb ->  "Response"
verb_response_relationship["type"] = "receives"
verb_response_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"Verb"}
verb_response_relationship["to_node"] = {"record_key":"_to_uid", "node_key":"uid", "node_label": "Response" }
verb_response_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
verb_response_relationship["records"] = []


# "RequestBody" -> Object
requestbody_object_relationship["type"] = "contains a"
requestbody_object_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"RequestBody"}
requestbody_object_relationship["to_node"] = {"record_key":"_to_uid", "node_key":"uid", "node_label": "Object" }
requestbody_object_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
requestbody_object_relationship["records"] = []

# "RequestBody" -> Field
requestbody_field_relationship["type"] = "contains a"
requestbody_field_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"RequestBody"}
requestbody_field_relationship["to_node"] = {"record_key":"_to_uid", "node_key":"uid", "node_label": "Field" }
requestbody_field_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
requestbody_field_relationship["records"] = []


# "Response" -> Object
response_object_relationship["type"] = "returns a"
response_object_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"Response"}
response_object_relationship["to_node"] = {"record_key":"_to_uid", "node_key":"uid", "node_label": "Object" }
response_object_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
response_object_relationship["records"] = []

# "Response" -> Field
response_field_relationship["type"] = "returns a"
response_field_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"Response"}
response_field_relationship["to_node"] = {"record_key":"_to_uid", "node_key":"uid", "node_label": "Field" }
response_field_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
response_field_relationship["records"] = []

# Parameters relationships
parameters_relationship["type"] = "has param"
parameters_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"Parameter"}
parameters_relationship["to_node"] = {"record_key":"_to_uid", "node_key":"uid", "node_label": "Parameter" }
parameters_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
parameters_relationship["records"] = []

# Parameters -> objects
parameters_object_relationship["type"] = "has object"
parameters_object_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"Parameter"}
parameters_object_relationship["to_node"] = {"record_key":"_to_uid", "node_key":"uid", "node_label": "Object" }
parameters_object_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
parameters_object_relationship["records"] = []

# Verb -> security relationship
verb_security_relationship["type"] = "secured by"
verb_security_relationship["from_node"] = {"record_key":"_from_uid","node_key":"uid","node_label":"Verb"}
verb_security_relationship["to_node"] = {"record_key":"_to_uid", "node_key":"uid", "node_label": "Security" }
verb_security_relationship["exclude_keys"] = ["_from_uid", "_to_uid"]
verb_security_relationship["records"] = []



if True:
	openapi_file = sys.argv[1] 


	print("============")
	print("OPEN API SPEC DOC: "+ openapi_file)
	with open(openapi_file, encoding="utf8") as my_file:
		if True:
			json_content = json.load(my_file)
			schemas = {}
			requestBodies = {}
			paths = {}
			securitySchemes = {}
			globalSecurity = {}
			optionalGSec = False
			GSecType = "non-oauth2"
			#popualte global security
			if "security" in json_content:
				globalSecurity = json_content["security"]
				print("****** GLOBAL SECURITY ******")
				for gsec in globalSecurity:
					if not gsec:
						optionalGSec = True
				for gsec in globalSecurity:
					if not gsec:
						continue
					#create globalsec objects (?)
					key = list(gsec.keys())[0]
					value = list(gsec.values())[0]
					security_record = {}
					security_record["uid"] = "global_security" 
					security_record["type"] = "security"
					security_record["name"] = key
					security_node["records"].append(security_record)
					if optionalGSec:
						print("Auth is optional")
					if value == []:
						GSecType = "non-oauth2"
					else:
						GSecType = "oauth2"
			#populate paths and components
			if "components" in json_content:
				if "schemas" in json_content["components"]:
					schemas = json_content["components"]["schemas"]
				if "securitySchemes" in json_content["components"]:
					securitySchemes = json_content["components"]["securitySchemes"]
				if "requestBodies" in json_content["components"]:
					requestBodies = json_content["components"]["requestBodies"]
			#create security schemas objects
			for securitySchema in securitySchemes:
				security_record = {}
				security_record["uid"] = "security_" + securitySchema
				security_record["type"] = "security"
				security_record["name"] = securitySchema
				security_node["records"].append(security_record)
			if "paths" in json_content:
				paths = json_content["paths"]
			for path in paths:
				path_record = {}
				path_record["uid"] = "path_" + path
				path_record["type"] = "path"
				path_record["name"] = path
				path_node["records"].append(path_record)
				if paths[path] is None:
					continue
				for path_verb in paths[path]:
					print("--------")
					print(path_verb + " " + path)
					#pp(paths[path][path_verb], depth=5, indent=4)
					verb_record = {}
					verb_record["uid"] = path_verb + "_" + path
					verb_record["type"] = "verb"
					verb_record["name"] = path_verb
					verb_node["records"].append(verb_record)
					#link paths with verbs
					relationship = {}
					relationship["_from_uid"] = path_record["uid"]
					relationship["_to_uid"] = verb_record["uid"]
					path_verb_relationship["records"].append(relationship)
					## there are 4 things to be extracted from paths: request, response, parameters and security schema
					if paths[path][path_verb] is None:
						continue
					if "parameters" in paths[path][path_verb]:
						parameters_record = {}
						parameters_record["uid"] = path_verb + "_" + path + "_parameters"
						parameters_record["type"] = "parameters"
						parameters_record["name"] = "params"
						parameter_node["records"].append(parameters_record)
						#link "Parameters" with the verb
						relationship = {}
						relationship["_from_uid"] = verb_record["uid"]
						relationship["_to_uid"] = parameters_record["uid"]
						verb_parameter_relationship["records"].append(relationship)
						for parameter in paths[path][path_verb]["parameters"]:
							if "type" in parameter:
								type_t = parameter["type"]
								parameter_record = {}
								parameter_record["uid"] = path_verb + "_" + path + "_parameter_" + type_t + "_" + parameter["name"]
								parameter_record["name"] =  type_t + "_" + parameter["name"]
								parameter_record["type"] = "parameter"
								parameter_node["records"].append(parameter_record)
								#print(parameter_record)
								# Create link between "Parameters" and the parameter object
								relationship = {}
								relationship["_from_uid"] = parameters_record["uid"]
								relationship["_to_uid"] = parameter_record["uid"]
								parameters_relationship["records"].append(relationship)
							elif "schema" in parameter:
								if "type" in parameter["schema"]:
									type_t = parameter["schema"]["type"]
									parameter_record = {}
									parameter_record["uid"] = path_verb + "_" + path + "_parameter_" + type_t + "_" + parameter["name"]
									parameter_record["name"] =  type_t + " " + parameter["name"]
									parameter_record["type"] = "parameter"
									#print(parameter_record)
									parameter_node["records"].append(parameter_record)
									# Create link between "Parameters" and the parameter object
									relationship = {}
									relationship["_from_uid"] = parameters_record["uid"]
									relationship["_to_uid"] = parameter_record["uid"]
									parameters_relationship["records"].append(relationship)
								elif "$ref" in parameter["schema"]:
									print("TODO: object as parameter")
									reference = parameter["schema"]["$ref"].split("/")
									ref = reference[len(reference) - 1]
									#Link object to params
									relationship = {}
									relationship["_from_uid"] = parameters_record["uid"]
									relationship["_to_uid"] = ref + "_object"
									print(relationship["_from_uid"] + " -> " + relationship["_to_uid"])
									parameters_object_relationship["records"].append(relationship)
									print(ref)
								else:
									print("WTF?")
							else:
								print("Can't find the type of parameter")
					## extract type of response
					if "responses" in paths[path][path_verb]:
						#print("response exists")
						responses_record = {}
						responses_record["uid"] = path_verb + "_" + path + "_responses"
						responses_record["name"] = "responses"
						responses_record["type"] = "responses"
						response_node["records"].append(responses_record)
						#link "responses" with the verb
						relationship = {}
						relationship["_from_uid"] = verb_record["uid"]
						relationship["_to_uid"] = responses_record["uid"]
						verb_response_relationship["records"].append(relationship)
						for response in paths[path][path_verb]["responses"]:
							#print("response: " + response)
							if "content" in paths[path][path_verb]["responses"][response]:
								for c in paths[path][path_verb]["responses"][response]["content"]:
									cnt = paths[path][path_verb]["responses"][response]["content"][c]
									if cnt is None:
										continue
									if "schema" not in cnt:
										print("SOMETHING WEIRD WITH THIS RESPONSE")
										continue
									if "$ref" in cnt["schema"]:
										reference = cnt["schema"]["$ref"].split("/")
										ref = reference[len(reference) - 1]
										# Create link between requestbody and object
										relationship = {}
										relationship["_from_uid"] = responses_record["uid"]
										relationship["_to_uid"] = ref + "_object"
										response_object_relationship["records"].append(relationship)
										#print("Creating link between " + responses_record["uid"] + " and " + ref + "_object")
									elif "type" in cnt["schema"]:
										if cnt["schema"]["type"] == "array":
											print("------>(1)response type is array")
										elif cnt["schema"]["type"] == "object":
											#This is not complete ... there may be other cases like "fields", etc.
											#print("------>(2)response type is object")
											#print(cnt)
											properties = {}
											if "properties" in cnt["schema"]:
												properties = cnt["schema"]["properties"]
											for prop in properties:
												if "$ref" in cnt["schema"]["properties"][prop]:
													#print(prop)
													#print(cnt["schema"]["properties"][prop]["$ref"])
													reference = cnt["schema"]["properties"][prop]["$ref"].split("/")
													ref = reference[len(reference) - 1]
													#Link response to object
													relationship = {}
													relationship["_from_uid"] = responses_record["uid"]
													relationship["_to_uid"] = ref + "_object"
													response_object_relationship["records"].append(relationship)
													#print(relationship)
										else:
											#create field node
											field_record = {}
											field_record["uid"] = path_verb + "_" + path + "_response_" + response
											field_record["name"] = cnt["schema"]["type"]
											field_record["type"] = "field"
											field_node["records"].append(field_record)
											#link field to object
											relationship = {}
											relationship["_from_uid"] = responses_record["uid"]
											relationship["_to_uid"] = field_record["uid"]
											response_field_relationship["records"].append(relationship)
											#print("------>(3)response type" + cnt["schema"]["type"])
											#print(relationship)
									elif "example" in cnt["schema"]:
										#create field node
										field_record = {}
										field_record["uid"] = path_verb + "_" + path + "_response_example_" + response
										field_record["name"] = "Example"
										field_record["value"] = str(cnt["schema"]["example"])
										field_record["type"] = "field"
										field_node["records"].append(field_record)
										#link field to object
										relationship = {}
										relationship["_from_uid"] = responses_record["uid"]
										relationship["_to_uid"] = field_record["uid"]
										response_field_relationship["records"].append(relationship)
										#print("Response example: " + str(cnt["schema"]["example"]))
										#print(relationship)
									else:
										print("Can't find the type of response")

					## extract type of request body
					if "requestBody" in paths[path][path_verb]:
						#print("requestBody exists")
						requestbody_record = {}
						requestbody_record["uid"] = path_verb + "_" + path + "_requestbody"
						requestbody_record["name"] = "body"
						requestbody_record["type"] = "body"
						requestbody_node["records"].append(requestbody_record)
						#link "responses" with the verb
						relationship = {}
						relationship["_from_uid"] = verb_record["uid"]
						relationship["_to_uid"] = requestbody_record["uid"]
						verb_requestbody_relationship["records"].append(relationship)
						print("Creating link between " + relationship["_from_uid"] + " and " + relationship["_to_uid"])
						for requestBody in paths[path][path_verb]["requestBody"]:
							print("requestBody: " + requestBody)
							if "$ref" in paths[path][path_verb]["requestBody"]:
								reference = paths[path][path_verb]["requestBody"]["$ref"].split("/")
								ref = reference[len(reference) - 1]
								# Create link between requestbody and object
								relationship = {}
								relationship["_from_uid"] = requestbody_record["uid"]
								relationship["_to_uid"] = ref + "_object"
								requestbody_object_relationship["records"].append(relationship)
								print("Creating link between " + requestbody_record["uid"] + " and " + ref + "_object")
							if "content" in paths[path][path_verb]["requestBody"]:
								for c in paths[path][path_verb]["requestBody"]["content"]:
									cnt = paths[path][path_verb]["requestBody"]["content"][c]
									#print(cnt)
									if "$ref" in cnt["schema"]:
										reference = cnt["schema"]["$ref"].split("/")
										ref = reference[len(reference) - 1]
										# Create link between requestbody and object
										relationship = {}
										relationship["_from_uid"] = requestbody_record["uid"]
										relationship["_to_uid"] = ref + "_object"
										requestbody_object_relationship["records"].append(relationship)
										print("Creating link between " + requestbody_record["uid"] + " and " + ref + "_object")
									elif "type" in cnt["schema"]:
										if cnt["schema"]["type"] == "array":
											pass
											print("------>(1)request type is array")
										elif cnt["schema"]["type"] == "object":
											print("------>(2)request type is array")
										else:
											field_record = {}
											field_record["uid"] = path_verb + "_" + path + "_requestbody_example_" + requestBody
											field_record["name"] = cnt["schema"]["type"]
											field_record["type"] = "field"
											field_node["records"].append(field_record)
											#link field to object
											relationship = {}
											relationship["_from_uid"] = requestbody_record["uid"]
											relationship["_to_uid"] = field_record["uid"]
											requestbody_field_relationship["records"].append(relationship)
											print("------>(3)request type" + cnt["schema"]["type"])
									elif "example" in cnt["schema"]:
										#create field node
										field_record = {}
										field_record["uid"] = path_verb + "_" + path + "_requestbody_example_" + requestBody
										field_record["name"] = "Example"
										field_record["value"] = str(cnt["schema"]["example"])
										field_record["type"] = "field"
										field_node["records"].append(field_record)
										#link field to object
										relationship = {}
										relationship["_from_uid"] = requestbody_record["uid"]
										relationship["_to_uid"] = field_record["uid"]
										requestbody_field_relationship["records"].append(relationship)
										#print("Reqyest body example: " + str(cnt["schema"]["example"]))
										#print(relationship)
									else:
										print("Can't find the type of request body")
					#if the path has it's own security rules, set those
					if "security" in paths[path][path_verb]:
						print("Path security found")
						for localSecurity in paths[path][path_verb]["security"]:
							optionalSec = False
							if not localSecurity:
								optionalSec = True
							if not localSecurity:
								continue
							#create localsec objects (?)
							key = list(localSecurity.keys())[0]
							print(key)
							value = list(localSecurity.values())[0]
							if optionalSec:
								print("Auth is optional")
								#link "Parameters" with the verb
							if localSecurity == []:
								relationship = {}
								relationship["_from_uid"] = verb_record["uid"]
								relationship["_to_uid"] = "security_" + key
								relationship["optional"] = optionalSec
								relationship["auth"] = "non-oauth2"
								relationship["type"] = "security"
								verb_security_relationship["records"].append(relationship)
								print("Non-OAuth2 Sec Req")
							else:
								relationship = {}
								relationship["_from_uid"] = verb_record["uid"]
								relationship["_to_uid"] = "security_" + key
								relationship["optional"] = optionalSec
								relationship["auth"] = "auth2"
								relationship["type"] = "security"
								verb_security_relationship["records"].append(relationship)
								print("OAuth2 Sec Req")
						#otherwise, if the path has no security rules, set the global rules if they exist
					elif globalSecurity:
							relationship = {}
							relationship["_from_uid"] = verb_record["uid"]
							relationship["_to_uid"] = "global_security"
							relationship["optional"] = optionalGSec
							relationship["auth"] = GSecType
							relationship["type"] = "security"
							verb_security_relationship["records"].append(relationship)


			## Parse the requestBodies
			if requestBodies is not None:
				print("Parsing request bodies..")
				#print(requestBodies)
				for requestBody in requestBodies:
					obj_record = {}
					obj_record["uid"] = requestBody + "_object"
					obj_record["name"] = requestBody
					obj_record["type"] = "object"
					object_node["records"].append(obj_record)
					print(obj_record)
					#print(requestBodies[requestBody]["content"])
					keys = list(requestBodies[requestBody]["content"].keys())
					#print(keys[0])
					#check if there is a "schema" defined inside the request body content
					if "schema" in requestBodies[requestBody]["content"][keys[0]]:
						schema = requestBodies[requestBody]["content"][keys[0]]["schema"]
					#if schema is empty, skip this object
					if schemas is None:
						continue
					if "properties" in schema:
						properties = schema["properties"]
					for prop in properties:
						print(prop)
						if "type" in properties[prop]:
							print("type")
							if properties[prop]["type"] == "array":
								if "items" not in properties[prop]:
									continue
								if "type" in properties[prop]["items"]:
									print("Todo array of things in requestbody")
								elif "$ref" in properties[prop]["items"]:
									print("Todo array of objects in requestbody")
								else:
									print("todo array of ??? in requestbody")
							else:
								print("fields in requestbody")
								#create field node
								field_record = {}
								field_record["uid"] = requestBody + "_" + properties[prop]["type"] + "_" + prop
								field_record["name"] = properties[prop]["type"] + " " + prop
								field_record["type"] = "field"
								field_node["records"].append(field_record)
								#link field to object
								relationship = {}
								relationship["_from_uid"] = obj_record["uid"]
								relationship["_to_uid"] = field_record["uid"]
								object_field_relationship["records"].append(relationship)
						elif "$ref" in properties[prop]:
							print("$ref")
						elif "allOf" in properties[prop]:
							print("allOf")
						elif "type" not in properties[prop] and "items" in properties[prop]:
							print("just an object, not an array of objects")
						else:
							print("undefined request body forma")
							print(properties[prop])
			## Parse the Object Schemas
			if schemas is not None:
				for schema in schemas:
					#print("----------")
					#print("\n")
					#print("***" + schema + "***") #all schemas/ojects
					obj_record = {}
					obj_record["uid"] = schema + "_object"
					obj_record["name"] = schema
					obj_record["type"] = "object"
					object_node["records"].append(obj_record)
					properties = {}
					if schemas[schema] is None:
						continue
					if "properties" in schemas[schema]:
						properties = schemas[schema]["properties"]
					for prop in properties:
						#print(prop)
						if "type" in properties[prop]:
							if properties[prop]["type"] == "array":
								if "items" not in properties[prop]:
									continue
								if "type" in properties[prop]["items"]:
									#create field node
									field_record = {}
									field_record["uid"] = schema + "_array_" + properties[prop]["items"]["type"] + "_" + prop
									field_record["name"] = "[" + properties[prop]["items"]["type"] + "]" + " " + prop
									field_record["type"] = "field"
									field_node["records"].append(field_record)
									#link field to object
									relationship = {}
									relationship["_from_uid"] = obj_record["uid"]
									relationship["_to_uid"] = field_record["uid"]
									object_field_relationship["records"].append(relationship)
								elif "$ref" in properties[prop]["items"]:
									reference = properties[prop]["items"]["$ref"].split("/")
									ref = reference[len(reference) - 1]
									#create field node
									field_record = {}
									field_record["uid"] = schema + "_array_" + ref + "_" + prop
									field_record["name"] = "[" + ref + "]" + " " + prop
									field_record["type"] = "field"
									field_node["records"].append(field_record)
									# object has field relationship
									relationship = {}
									relationship["_from_uid"] = obj_record["uid"]
									relationship["_to_uid"] = field_record["uid"]
									object_field_relationship["records"].append(relationship)
									# field of type object relationship
									relationship = {}
									relationship["_from_uid"] = field_record["uid"]
									relationship["_to_uid"] = ref + "_object"
									field_object_relationship["records"].append(relationship)
								else:
									print("SOME WEIRD ARRAY oF ARRAY of ARRAY....")
							else:
								#print(properties[prop]["type"] + " " + prop)
								#create field node
								field_record = {}
								field_record["uid"] = schema + "_" + properties[prop]["type"] + "_" + prop
								field_record["name"] = properties[prop]["type"] + " " + prop
								field_record["type"] = "field"
								field_node["records"].append(field_record)
								#link field to object
								relationship = {}
								relationship["_from_uid"] = obj_record["uid"]
								relationship["_to_uid"] = field_record["uid"]
								object_field_relationship["records"].append(relationship)
						# here is not good
						elif "$ref" in properties[prop]:
							reference = properties[prop]["$ref"].split("/")
							ref = reference[len(reference) - 1]
							#print("[" + ref + "]" + " " + prop)
							#create field node
							field_record = {}
							field_record["uid"] = schema + "_" + ref + "_" + prop
							field_record["name"] = ref + " " + prop
							field_record["type"] = "field"
							field_node["records"].append(field_record)
							# object has field relationship
							relationship = {}
							relationship["_from_uid"] = obj_record["uid"]
							relationship["_to_uid"] = field_record["uid"]
							object_field_relationship["records"].append(relationship)
							# field of type object relationship
							relationship = {}
							relationship["_from_uid"] = field_record["uid"]
							relationship["_to_uid"] = ref + "_object"
							field_object_relationship["records"].append(relationship)
						elif "allOf" in properties[prop]:
							#create field node
							field_record = {}
							field_record["uid"] = schema + "_alloff_" + prop
							field_record["name"] = "Any " + prop
							field_record["type"] = "field"
							field_node["records"].append(field_record)
							# object has field relationship
							relationship = {}
							relationship["_from_uid"] = obj_record["uid"]
							relationship["_to_uid"] = field_record["uid"]
							object_field_relationship["records"].append(relationship)
							# field can be of multiple types - create a relationship towards each possible type
							for e in properties[prop]["allOf"]:
								#TODO here we can have both "type" and "$ref", not just "$ref"
								reference = e["$ref"].split("/")
								ref = reference[len(reference) - 1]
								# create relationship
								relationship = {}
								relationship["_from_uid"] = field_record["uid"]
								relationship["_to_uid"] = ref + "_object"
								field_object_relationship["records"].append(relationship)
						elif "type" not in properties[prop] and "items" in properties[prop]: # just an object, not an array of objects
							if "$ref" not in properties[prop]["items"]:
								continue
							reference = properties[prop]["items"]["$ref"].split("/")
							ref = reference[len(reference) - 1]
							#create field node
							field_record = {}
							field_record["uid"] = schema + ref + "_" + prop
							field_record["name"] = ref +  " " + prop
							field_record["type"] = "field"
							field_node["records"].append(field_record)
							# object has field relationship
							relationship = {}
							relationship["_from_uid"] = obj_record["uid"]
							relationship["_to_uid"] = field_record["uid"]
							object_field_relationship["records"].append(relationship)
							# field of type object relationship
							relationship = {}
							relationship["_from_uid"] = field_record["uid"]
							relationship["_to_uid"] = ref + "_object"
							field_object_relationship["records"].append(relationship)
						else:
							print("??????")
							print(properties[prop])
		else:
			pass
#except:
#	print("[!] Error in parsing OpenAPI JSON file")

#print(json.dumps(neo4j_data, indent=4))

try:
	with open('neo4j/my_neo4j.json', 'w') as f:
		json.dump(neo4j_data, f, indent=4)
except:
	print("[!] Error writing the file")



