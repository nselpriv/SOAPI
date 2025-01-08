# SOAPI - Scanning OpenAPIs

Map OpenAPI documentations as Neo4J graphs and uncover vulnerabilities in the design implementation of the API. 

SOAPI helps you detect sensitive data exposure, public endpoint leaks and rate-limiting bypasses through graph traversal techniques - a Bloodhound for APIs.

Developed for OWASP Copenhagen 2024 and Disobey 2025 conferences - recordings coming soon!

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
[------------------------------]

[+] Stats:

There are 25 unique endpoints
 - 14 public endpoints
 - 11 protected endpoints

[------------------------------]

[+] IDOR ID Finder:

[*] post_/v1/signin
string username
 -> post /v1/signin
 -> get /v1/check
 -> get /v1/user/:{username}

[*] post_/v1/signup
string username
 -> post /v1/signin
 -> get /v1/check
 -> get /v1/user/:{username}

[------------------------------]

[+] List objects accessible through public & private endpoints

[+] serverError
Public: post /v1/signin
Public: get /v1/user
Public: get /v1/user/:{username}
Public: get /v1/event
Public: get /v1/event/:{uuid}
Public: get /v1/multimedia/image
Public: get /v1/multimedia/video
Public: get /v1/report
Public: get /v1/report/info
Public: get /v1/stat
Protected: post /v1/signup
Protected: get /v1/check
Protected: delete /v1/user/:{username}
Protected: delete /v1/event/:{uuid}
Protected: patch /v1/event/comment
Protected: post /v1/report
Protected: patch /v1/report/info
Protected: delete /v1/report/info

[+] unsupportedMediaType415
Public: post /v1/signin
Protected: post /v1/signup
Protected: put /v1/event
Protected: patch /v1/event/comment
Protected: patch /v1/jetson/docker
Protected: patch /v1/jetson/image
Protected: post /v1/report
Protected: patch /v1/report/info
Protected: delete /v1/report/info

[------------------------------]

[+] List public readble fields

----
POST /v1/signin
[-] string accessToken
[-] string username
[-] string error
----
GET /v1/user
[-] [string] users
[-] string error
----
GET /v1/user/:{username}
[-] string username
[-] string first_name
[-] string last_name
[-] string role
[-] string error
[-] string error
----
GET /v1/event/:{uuid}
[-] string uid
[-] integer number
[-] string side
[-] integer brigade
[-] string video_path
[-] string image_path
[-] string start_time
[-] string end_time

[------------------------------]

[+] List public endpoints

post /v1/signin
get /v1/user
get /v1/user/:{username}
get /v1/event
get /v1/event/:{uuid}
get /v1/event/status
get /v1/jetson/docker
get /v1/jetson/image
get /v1/multimedia/stream
get /v1/multimedia/image
get /v1/multimedia/video
get /v1/report
get /v1/report/info
get /v1/stat
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
