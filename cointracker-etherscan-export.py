import requests
import json
import configparser
import datetime

# load credentials from config
config = configparser.ConfigParser()
config.read('credentials.ini')
# credentials
address = config['evm']['address']
url_base = config['evm']['scan_url']
gas_token = config['evm']['gas_token']
gas_decimal = int(config['evm']['gas_decimal'])
api_key = "YourApiKeyToken"

# urls for requests
url_normal="{}/api?module=account&action=txlist&address={}&sort=asc&apikey={}".format(url_base, address, api_key)
url_erc20="{}/api?module=account&action=tokentx&address={}&sort=asc&apikey={}".format(url_base, address, api_key)

# normal transactions
response = requests.get(url_normal)
for item in response.json()["result"]:
    # Relevant keys: timeStamp, from, to, value, tokenDecimal, tokenSymbol, gasPrice, gasUsed
    if (int(item['value']) == 0): continue
    decimals = gas_decimal
    timestamp = datetime.datetime.utcfromtimestamp(int(item['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')
    value_proper = int(item['value']) * pow(10, -decimals)
    gas_proper = int(item['gasUsed']) * int(item['gasPrice']) * pow(10, -decimals) * 0.5
    symbol = gas_token
    dir = 'in ' if item['to'].casefold() == address.casefold() else 'out'
    print("{}: {}, {}, {}, {}, {}".format(dir, timestamp, value_proper, symbol, gas_proper, gas_token))


# token transactions
response = requests.get(url_erc20)
for item in response.json()["result"]:
    # Relevant keys: timeStamp, from, to, value, tokenDecimal, tokenSymbol, gasPrice, gasUsed
    decimals = int(item['tokenDecimal'])
    timestamp = datetime.datetime.utcfromtimestamp(int(item['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')
    value_proper = int(item['value']) * pow(10, -decimals)
    gas_proper = int(item['gasUsed']) * int(item['gasPrice']) * pow(10, -decimals) * 0.5
    symbol = item['tokenSymbol']
    dir = 'in ' if item['to'].casefold() == address.casefold() else 'out'
    print("{}: {}, {}, {}, {}, {}".format(dir, timestamp, value_proper, symbol, gas_proper, gas_token))
