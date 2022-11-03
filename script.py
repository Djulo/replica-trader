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
        replica_balance = replica.fetch_balance()['USD']['free']
        account_balance = account.fetch_balance()['USD']['free']
        factor = replica_balance / account_balance

        replica_positions = replica.fetch_positions()
        replica_positions = replica.index_by(replica_positions, 'symbol')

        account_positions = replica.fetch_positions()
        account_positions = account.index_by(account_positions, 'symbol')

        orders = replica.fetch_orders(since=since)
        orders_to_create = [x for x in orders if x not in account_orders]
        orders_to_create = replica.sort_by(orders_to_create, 'timestamp')

        if len(orders_to_create) > 0:
            since = orders_to_create[-1]['timestamp']

        for order in orders_to_create:
            amount = order['amount'] / factor

            account.load_markets()
            market = account.market(order['symbol'])
            if amount < market['limits']['amount']['min']:
                amount = market['limits']['amount']['min']

            replica_position = replica_positions.get(order['symbol'], None)
            account_position = account_positions.get(order['symbol'], None)
            if replica_position is not None and \
               account_position is not None and \
               order['amount'] == replica_position['info']['size']:
                amount = account_position['info']['size']

            order = account.create_order(order['symbol'], order['type'], order['side'], amount, ...)

        account_orders.extend(orders_to_create)
        time.sleep(2)
    except ccxt.NetworkError as e:
        print(e)  # retry on next iteration
    except ccxt.ExchangeError as e:
        print(e)
    except Exception as e:
        print(e)
