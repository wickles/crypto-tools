import requests
import json

# insert credentials here
address=""

# urls for requests
url_normal="https://api.arbiscan.io/api?module=account&action=txlist&address={}&sort=asc&apikey=YourApiKeyToken".format(address)
url_erc20="https://api.arbiscan.io/api?module=account&action=tokentx&address={}&sort=asc&apikey=YourApiKeyToken".format(address)

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
