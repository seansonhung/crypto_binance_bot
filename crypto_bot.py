from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
from time import sleep

def decimal_formatter(number):
    #change float number to string format and get rid of scientific notation
    return format(number, '.8f')

def get_closing_price(client, sym_pair):
    # fetch 1 minute klines for the last day up until now
    klines = client.get_historical_klines(sym_pair, Client.KLINE_INTERVAL_1MINUTE, "1 min ago")
    most_recent = klines.pop()
    last_closing_price = float(most_recent[4])
    return last_closing_price

def target_profit(history_file):
    # 1 % increased in amount of coin after 2 transactions, before fees
    # inital balance is from historical data, 1 transaction ago.
    percent_profit = 0.01
    f= open(history_file)
    contents = f.readlines()
    initial_balance = float(contents[1].split()[0])
    f.close()
    target_balance = float(initial_balance) + (float(initial_balance) * percent_profit)
    return target_balance

def target_price_met(asset_sym, asset_balance, target_balance, last_closing_price, pair_sym):
    #Calculate price of altcoin/btc pair needed to turn asset balance to target balance
    price_met = False
    target_price = 999
    if (asset_sym == 'BTC'):
        target_price = asset_balance/target_balance
        price_met = (last_closing_price <= target_price) 
    else:
        target_price = target_balance/asset_balance
        price_met = (last_closing_price >= target_price)	
    print("target_price {}, closing price {} for {}".format(decimal_formatter(target_price), decimal_formatter(last_closing_price), pair_sym))
    return price_met
        
def edit_history(history_file, balance, sym):
    # write to the history file of the new amount of coins
        f = open(history_file,'r+')
        lines = f.readlines() # read old content
        f.seek(0) # go back to the beginning of the file
        f.write("{} {} \n".format(balance, sym)) # write new content at the beginning
        for line in lines: # write old content after new
            f.write(line)
        f.close()
        print("successful trade, {} {} is the new balance.".format(balance, sym))
        
def buy_sell_order(client, sell, asset_sym, buy_sell_quantity, last_closing_price, pair_sym):
    #sell order if true
    if (sell):
        client.order_limit_sell(symbol= pair_sym, timeInForce = "GTC", quantity=buy_sell_quantity, price=decimal_formatter(last_closing_price))
    #buy order if false
    else:
        client.order_limit_buy(symbol= pair_sym, timeInForce = "GTC", quantity=buy_sell_quantity, price=decimal_formatter(last_closing_price))
    print("order is place.")
        
def confirm_order(client, pair_sym):
    confirm = False
    while not confirm:
        order = client.get_open_orders(symbol = pair_sym)
        if not order:
            confirm = True
    print("order is confirmed")
    
def get_syms_and_balance(history_file):
    # get balance and target
    f= open(history_file)
    contents = f.readlines()
    f.close()    
    asset_sym = contents[0].split()[1]
    target_sym = contents[1].split()[1]  
    asset_balance = float(contents[0].split()[0]) #asset_balance = float(client.get_asset_balance(asset = asset_sym)['free'])
    target_balance = float(target_profit(history_file))   
    return(asset_sym, target_sym, asset_balance, target_balance)
    
def ETHBTC_bot(client):
    pair_sym = "ETHBTC"
    # get balance and target
    (asset_sym, target_sym, asset_balance, target_balance) = get_syms_and_balance("ETHBTC_HISTORY.txt")
    
    try:
        last_closing_price = get_closing_price(client, pair_sym)
	# check buy/sell condition
        trade_condition_sastified = target_price_met(asset_sym, asset_balance, target_balance, last_closing_price, pair_sym)
        if (trade_condition_sastified):
            print("trading price met")
	    # get the quantity to sell or buy
            buy_sell_quantity = 0
            sell = False
            if (asset_sym == "ETH"):
                sell = True
                buy_sell_quantity = round(float(asset_balance) - 0.001, 3) # rounding according to lotz size
            else:
                buy_sell_quantity = round(float(target_balance) - 0.001, 3)
            buy_sell_order(client, sell, asset_sym, buy_sell_quantity, last_closing_price, pair_sym)
            confirm_order(client, pair_sym)
            sleep(5)
            #edit history
            new_balance = float(client.get_asset_balance(asset = target_sym)['free'])
            edit_history("ETHBTC_HISTORY.txt",new_balance, target_sym)

    except BinanceAPIException as e:
        print(e.status_code)
        print(e.message)	    
	    
def XRPBTC_bot(client):
    pair_sym = "XRPBTC"
    # get balance and target
    (asset_sym, target_sym, asset_balance, target_balance) = get_syms_and_balance("XRPBTC_HISTORY.txt")
    try:
        last_closing_price = get_closing_price(client, pair_sym)
	# check buy/sell condition
        trade_condition_sastified = target_price_met(asset_sym, asset_balance, target_balance, last_closing_price, pair_sym)
        if (trade_condition_sastified):
            print("trading price met")
	    # get the quantity to sell or buy
            buy_sell_quantity = 0
            sell = False
            if (asset_sym == "XRP"):
                sell = True
                buy_sell_quantity = int(asset_balance)# rounding according to lotz size
            else:
                buy_sell_quantity = int(target_balance)
            buy_sell_order(client, sell, asset_sym, buy_sell_quantity, last_closing_price, pair_sym)
            confirm_order(client, pair_sym)
            sleep(5)
            #edit history
            new_balance = float(client.get_asset_balance(asset = target_sym)['free'])
            edit_history("XRPBTC_HISTORY.txt",new_balance, target_sym)
	    		
    except BinanceAPIException as e:
        print(e.status_code)
        print(e.message)    
    

def main():
    api_secret = ""
    api_key = ""
    
    print("program started")
    client = Client(api_key, api_secret, {"timeout": 100})
    
    while True:
        ETHBTC_bot(client)
        XRPBTC_bot(client)
        # check price every 100s
        sleep(100)	    

if  __name__ =='__main__':main()