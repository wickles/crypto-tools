import requests
import json

# insert credentials here
address=""
api_key="YourApiKeyToken"

# urls for requests
url_base="https://api.arbiscan.io"
url_normal="{}/api?module=account&action=txlist&address={}&sort=asc&apikey={}".format(url_base, address, api_key)
url_erc20="{}/api?module=account&action=tokentx&address={}&sort=asc&apikey={}".format(url_base, address, api_key)

# normal transactions
#response = requests.get(url_normal)
#print(response.json()["result"])
#for item in response.json()["result"]:
#    print("blah")

# token transactions
response = requests.get(url_erc20)
# do stuff
#print(response.json()["result"])
for item in response.json()["result"]:
    print("{} {} {} {}".format(item["timeStamp"], item["value"], item["tokenSymbol"], item["gas"]))
