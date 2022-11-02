import ccxt
from config import replica, account
import time
import pprint

replica = ccxt.ftx({
    'apiKey': replica['apiKey'],
    'secret': replica['secret'],
    'headers': {
        'FTX-SUBACCOUNT': replica['subaccount']
    }
})

account = ccxt.ftx({
    'apiKey': account['apiKey'],
    'secret': account['secret'],
    'headers': {
        'FTX-SUBACCOUNT': account['subaccount']
    }
})

since = time.time() * 1000 - 1000 * 60 * 60

orders = replica.fetch_orders()
account_orders = [x for x in orders if x['timestamp'] < since]

while True:
    try:
        replica_balance = replica.fetch_balance()['USD']['free']
        account_balance = account.fetch_balance()['USD']['free']
        factor = replica_balance / account_balance

        orders = replica.fetch_orders(since=since)

        orders_to_create = [x for x in orders if x not in account_orders]
        orders_to_create = replica.sort_by(orders_to_create, 'timestamp')
        if len(orders_to_create) > 0:
            since = orders_to_create[-1]['timestamp']

        for order in orders:
            amount = order['amount'] / factor
            order = account.create_order(order['symbol'], order['type'], order['side'], amount, ...)

        account_orders.extend(orders_to_create)
        time.sleep(2)
    except ccxt.NetworkError as e:
        print(e)  # retry on next iteration
    except ccxt.ExchangeError as e:
        print(e)
    except Exception as e:
        print(e)
