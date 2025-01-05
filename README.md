# SOAPI
SOAPI - Scanning OpenAPIs, one documentation at a time

Check out the [SquareSec SOAPI Guide](https://www.sqrsec.com/soapi-guide) to see how to use it

![image](https://github.com/user-attachments/assets/bede7a1f-f5f1-4fe2-9e34-df2985cd5a69)



## 1. Installation
```
git clone https://github.com/andrei8055/SOAPI/
cd SOAPI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 soapi.py
```

## 2. Config
1. Set up your Neo4j DB (you can use the sandbox for free)
2. Extract URL, username and password
3. Place them in the `config.py` file
```
neo4j_config = {
    "uri": "bolt://127.0.0.1",
    "username": "neo4j",
    "password": "<password>"
}
```

## 3. Running
1. Drop your openapi.json file(s) in the `/samples` folder
2. Run `python3 soapi.py`
```
python3 soapi.py 

███████╗ ██████╗  █████╗ ██████╗ ██╗
██╔════╝██╔═══██╗██╔══██╗██╔══██╗██║
███████╗██║   ██║███████║██████╔╝██║
╚════██║██║   ██║██╔══██║██╔═══╝ ██║
███████║╚██████╔╝██║  ██║██║     ██║
╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝
                                    

[------------------------------]
[+] Cleaning Neo4j DB..
[+] Neo4j DB deleted!
[+] Analyzing samples/3074.json
[+] Parsing complete!
[+] Uploading data to Neo4j server..
[+] Data uploaded succesfully!
[+] Checking vulnerable paths..

[+] Checking for objects accessible through public & private endpoints

[+++++] Object serverError_object can be reached from public & protected endpoints
[+++++] Object unsupportedMediaType415_object can be reached from public & protected endpoints
[+++++] Object invalidQuery_object can be reached from public & protected endpoints
[+++++] Object eventNF_object can be reached from public & protected endpoints
[+++++] Object userNF_object can be reached from public & protected endpoints

[+] Checking for public accessible objects..

[Public Read] Object bigList_object can be reached from 'GET /v1/multimedia/stream'
[Public Read] Object image_object can be reached from 'GET /v1/multimedia/image'
[Public Read] Object video_object can be reached from 'GET /v1/multimedia/video'
[Public Read] Object resourceNF_object can be reached from 'GET /v1/multimedia/image'
[Public Read] Object resourceNF_object can be reached from 'GET /v1/multimedia/video'
[Public Read] Object multimedia400_object can be reached from 'GET /v1/multimedia/image'
[Public Read] Object multimedia400_object can be reached from 'GET /v1/multimedia/video'
[Public Modify] Object signInResponse_object can be reached from POST /v1/signin'
[Public Modify] Object signInResponse401_object can be reached from POST /v1/signin'
```

## 4. Analyze
1. Given a field/object - get all paths to there starting from the endpoint

```
MATCH (start), (end {uid: "UserEmail"})
WHERE start.uid STARTS WITH "path_"
MATCH path = (start)-[*..10]->(end)
RETURN path

```


2. Find path between 2 nodes

```
MATCH path = (start {uid: "User_object"})-[*1..5]-(end {uid: "UserEmail_string"})
RETURN path
```

3. Find a specific object and it's links
```
MATCH (n {uid: "Account_object"})-[r]-(connected)
RETURN n, r, connected

```


4. Delete everything from Neo4J

```
MATCH (n)
DETACH DELETE n;
```

5. View the whole OpenAPI as a graph
```
MATCH (n)
RETURN n
LIMIT 5000
```

![image](https://github.com/user-attachments/assets/3a7f80a0-81c4-463d-ac31-3c7e2de2235c)
