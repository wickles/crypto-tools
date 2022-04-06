from typing import Text
import requests
import json
import csv
import configparser
import datetime

# load credentials from config
config = configparser.ConfigParser()
config.read('credentials.ini')
# credentials
address = config['evm']['address']
api_key = config['evm']['api_key']
url_base = config['evm']['scan_url']
gas_token = config['evm']['gas_token']
gas_decimal = int(config['evm']['gas_decimal'])
# edge cases
edge_arb_dom = 'api.arbiscan.io'
edge_arb_mint = '0x000000000000000000000000000000000000006E'

# urls for requests
url_normal="{}/api?module=account&action=txlist&address={}&sort=asc&apikey={}".format(url_base, address, api_key)
url_erc20="{}/api?module=account&action=tokentx&address={}&sort=asc&apikey={}".format(url_base, address, api_key)

# Build URL for receipt of a given tx hash
def txReceiptUrl(hash):
    return "{}/api?module=proxy&action=eth_getTransactionReceipt&txhash={}&apikey={}".format(url_base, hash, api_key)

# Write Header
csvfile = open('trades.csv', 'w', newline='')
writer = csv.writer(csvfile)
writer.writerow(['Date', 'Received Quantity', 'Received Currency', 'Sent Quantity', 'Sent Currency', 'Fee Amount', 'Fee Currency', 'Tag'])

# normal transactions
response = requests.get(url_normal)
results = response.json()["result"]
index = 0
for item in results:
    index += 1

    # Relevant keys: timeStamp, from, to, value, tokenDecimal, tokenSymbol, gasPrice, gasUsed, input
    #if (int(item['value']) == 0): continue
    #decimals = gas_decimal
    timestamp = datetime.datetime.utcfromtimestamp(int(item['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')
    value_proper = int(item['value']) * pow(10, -gas_decimal)
    symbol = gas_token

    edge_arb_condition = item['from'].casefold() == address.casefold() and \
                         item['to'].casefold() == edge_arb_mint.casefold() and \
                         url_base.casefold().find(edge_arb_dom) != -1
    if item['to'].casefold() == address.casefold() or edge_arb_condition:
        # received, no gas cost
        gas_proper = '0'
        # Write line to file
        writer.writerow([timestamp, value_proper, symbol, '', '', gas_proper, gas_token, ''])
    else: # sent, need to get gas cost
        # Query transaction receipt for effective gas price
        print("Query ({} / {}): {}".format(index, len(results), item['hash']))
        for attempts in range(5):
            try:
                url_tx = txReceiptUrl(item['hash'])
                resp_tx = requests.get(url_tx)
                item_tx = resp_tx.json()["result"]
                gas_proper = int(item['gasUsed']) * int(item_tx['effectiveGasPrice'],0) * pow(10, -gas_decimal)
            except:
                print("Error occurred while handling query...")
            else:
                break
        else:
            print("Timedout handling that query!")

        # Write line to file
        writer.writerow([timestamp, '', '', value_proper, symbol, gas_proper, gas_token, ''])

# token transactions
response = requests.get(url_erc20)
results = response.json()["result"]
index = 0
for item in results:
    index += 1

    # Collect relevant values
    token_decimal = int(item['tokenDecimal'])
    timestamp = datetime.datetime.utcfromtimestamp(int(item['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')
    value_proper = int(item['value']) * pow(10, -token_decimal)
    symbol = item['tokenSymbol']

    # Query transaction receipt for effective gas price
    print("Query ({} / {}): {}".format(index, len(results), item['hash']))
    url_tx = txReceiptUrl(item['hash'])
    resp_tx = requests.get(url_tx)
    item_tx = resp_tx.json()["result"]
    gas_proper = int(item['gasUsed']) * int(item_tx['effectiveGasPrice'],0) * pow(10, -gas_decimal)

    # Write line to file
    if item['to'].casefold() == address.casefold(): #received
        writer.writerow([timestamp, value_proper, symbol, '', '', gas_proper, gas_token, ''])
    else: # sent
        writer.writerow([timestamp, '', '', value_proper, symbol, gas_proper, gas_token, ''])
