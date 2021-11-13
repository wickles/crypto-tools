import datetime
import json
import logging
import csv

import sys
sys.path.append('ext/okcoin-V3-Open-API-SDK/okcoin-python-sdk-api')

import okcoin.account_api as account
import okcoin.fiat_api as fiat
import okcoin.lever_api as lever
import okcoin.spot_api as spot
import okcoin.status_api as status
import okcoin.Oracl_api as oracle

log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='mylog-rest.json', filemode='a', format=log_format, level=logging.INFO)


def get_timestamp():
    now = datetime.datetime.now()
    t = now.isoformat("T", "milliseconds")
    return t + "Z"


def format_date(timestamp):
    return datetime.datetime.fromisoformat(timestamp.replace('Z','')).isoformat(sep=' ')


time = get_timestamp()

if __name__ == '__main__':
    # fill in API credentials here
    api_key = ""
    secret_key = ""
    passphrase = ""
    '''
     param use_server_time's value is False if is True will use server timestamp
    '''
    # ACCOUNT API
    accountAPI = account.AccountAPI(api_key, secret_key, passphrase, False)

    # SPOT API
    spotAPI = spot.SpotAPI(api_key, secret_key, passphrase, False)

    empty = ''
    with open('trades.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Received Quantity', 'Received Currency', 'Sent Quantity', 'Sent Currency', 'Fee Amount', 'Fee Currency', 'Tag'])

        # get all funding account transactions from paginated queries
        cursor = ''
        results = []
        while True:
            result, resp = accountAPI.get_ledger_record(after=cursor)
            logging.info("result:" + json.dumps(result))
            results.extend(result)
            print("response:", resp)
            if 'after' in resp:
                cursor = resp['after']
            else:
                break

        # write funding account transactions to csv, ignoring internal transfers
        prev = None
        for entry in results:
            if entry['typename'] == 'exchange':
                if prev is None:
                    prev = entry
                else:
                    if float(entry['amount']) < 0:
                        send, recv = entry, prev
                    else:
                        send, recv = prev, entry
                    writer.writerow([format_date(entry['timestamp']), recv['amount'], recv['currency'], send['amount'], send['currency'], send['fee'], send['currency'], empty])
                    prev = None
            # activity = promo. empty = staking transaction or reward.
            elif entry['typename'] in {'Deposit', 'withdrawal', 'Get from activity', ''}:
                if float(entry['amount']) < 0:
                    writer.writerow([format_date(entry['timestamp']), empty, empty, entry['amount'], entry['currency'], entry['fee'], entry['currency'], empty])
                else:
                    writer.writerow([format_date(entry['timestamp']), entry['amount'], entry['currency'], empty, empty, entry['fee'], entry['currency'], empty])

        # get all fills from paginated queries
        cursor = ''
        results = []
        while True:
            result, resp = spotAPI.get_fills('', from_c=cursor)
            logging.info("result:" + json.dumps(result))
            results.extend(result)
            print("response:", resp)
            if 'after' in resp:
                cursor = resp['after']
            else:
                break

        # write fills to csv
        for entry in results:
            # sell should come first
            if entry['side'] == 'sell':
                sell = entry
            # buy should come second
            elif entry['side'] == 'buy':
                buy = entry
                if (buy['order_id'] != sell['order_id']):
                    logging.info("order ID mismatch (sell/buy):" + sell['order_id'] + "/" + buy['order_id'])
                else:
                    writer.writerow([format_date(entry['timestamp']), buy['size'], buy['currency'], sell['size'], sell['currency'], buy['fee'], buy['currency'], empty])
