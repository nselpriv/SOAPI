import os
import requests
import json
import re

banner = """
███████╗ ██████╗  █████╗ ██████╗ ██╗
██╔════╝██╔═══██╗██╔══██╗██╔══██╗██║
███████╗██║   ██║███████║██████╔╝██║
╚════██║██║   ██║██╔══██║██╔═══╝ ██║
███████║╚██████╔╝██║  ██║██║     ██║
╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝
                                    
"""
print(banner)

directory = "samples"

for filename in os.scandir(directory):
	if filename.is_file():
		print("[------------------------------]")
		print("[+] Cleaning Neo4j DB..")
		os.system('python3 clean.py ' + filename.path)
		print("[+] Neo4j DB deleted!")

		print("[+] Analyzing " + filename.path)
		os.system('python3 parse.py ' + filename.path + ' >nul 2>&1')
		print("[+] Parsing complete!")

		print("[+] Uploading data to Neo4j server..")
		os.system('python3 upload.py')
		print("[+] Data uploaded succesfully!")

		print("[+] Checking vulnerable paths..")
		os.system('python3 scan.py')
		print("[+] Check complete!")