#-----Description: This Script Forces a refresh of a Plex Media Server's Libraries via the Plex API. 
#-------You'll Need an API key that is retrieved from your Media Server by Selecting a Movie/Show and viewing the XML data
#----------The Key can be extracted from the XML Data 

import requests

# Set your URL, port, and Plex Token
URL = "yourddns.address.com" # <----Enter your DDNS Address # 
PORT = "32400"               # <<<---- Default Port for Plex Server
PLEX_TOKEN = "XXXXXXXxxxxxxxxxXXXX" # <<<---Retrieve from your Media Server

# Set headers including the X-Plex-Token
headers = {
    "X-Plex-Token": PLEX_TOKEN
}

# Make a GET request with the X-Plex-Token header
response = requests.get(f"http://{URL}:{PORT}/library/sections/all/refresh", headers=headers)

# Check for success and print the result
if response.status_code == 200:
    print("Success:", response.text)
else:
    print("Error:", response.status_code)
