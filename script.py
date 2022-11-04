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

since = None
account_orders = replica.fetch_orders()

while True:
    try:
        orders = replica.fetch_orders(since=since)
        orders_to_create = [x for x in orders if x not in account_orders]
        orders_to_create = replica.sort_by(orders_to_create, 'timestamp')

        for order in orders_to_create:
            replica_balance = replica.fetch_balance()['USD']['free']
            account_balance = account.fetch_balance()['USD']['free']

            factor = replica_balance / account_balance
            amount = order['amount'] / factor

            account.load_markets()
            market = account.market(order['symbol'])

            if amount < market['limits']['amount']['min']:
                amount = market['limits']['amount']['min']

            position = next((x for x in replica.fetch_positions() if x['symbol'] == order['symbol']), None)
            if position is not None and position['info']['size'] == order['amount']:
                position = next((x for x in account.fetch_positions() if x['symbol'] == order['symbol']), None)
                if position is not None:
                    amount = position['info']['size']

            res = account.create_order(order['symbol'], order['type'], order['side'], amount, ...)
            since = order['timestamp']
            account_orders.append(order)
    except ccxt.NetworkError as e:
        print(e)  # retry on next iteration
    except ccxt.ExchangeError as e:
        print(e)
    except Exception as e:
        print(e)
