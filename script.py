import ccxt
from config import replica, account
import time
import pprint

exchange_id = 'ftx'
exchange_class = getattr(ccxt, exchange_id)
replica = exchange_class({
    'apiKey': replica['apiKey'],
    'secret': replica['secret'],
    'headers': {
        'FTX-SUBACCOUNT': replica['subaccount']
    }
})

account = exchange_class({
    'apiKey': account['apiKey'],
    'secret': account['secret'],
    'headers': {
        'FTX-SUBACCOUNT': account['subaccount']
    }
})

account_orders = replica.fetchOrders()

while True:
    replica_balance = replica.fetchBalance()['USD']['free']
    account_balance = account.fetchBalance()['USD']['free']
    factor = replica_balance / account_balance

    replica_orders = replica.fetchOrders()
    orders = [x for x in replica_orders if x not in account_orders]

    for order in orders:
        try:
            amount = order['amount'] / factor
            order = account.createOrder(order['symbol'], order['type'], order['side'], amount, ...)
			pprint(order)
        except:
            pass

    account_orders = replica_orders
    time.sleep(2)
