from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
from time import sleep

def target_profit():
    # 0.7 % increased in amount of coin after 2 transactions, before fees
    # inital balance is from historical data, 1 transaction ago.
    percent_profit = 0.007
    f= open("HISTORY.txt")
    contents = f.readlines()
    initial_balance = float(contents[1].split()[0])
    f.close()
    target_balance = float(initial_balance) + (float(initial_balance) * percent_profit)
    return target_balance

def target_price_met(asset_sym, asset_balance, target_balance, last_closing_price ):
    #Calculate price of eth/btc needed to turn asset balance to target balance
    price_met = False
    target_price = 999
    if (asset_sym == 'ETH'):
        target_price = target_balance/asset_balance
        price_met = (last_closing_price >= target_price)
    else:
        target_price = asset_balance/target_balance
        price_met = (last_closing_price <= target_price)
    print("target_price {}, closing price {}".format(target_price, last_closing_price))
    return price_met
        
def edit_history(balance, sym):
    # write to the history file of the new amount of coins
        f = open('HISTORY.txt','r+')
        lines = f.readlines() # read old content
        f.seek(0) # go back to the beginning of the file
        f.write("{} {} \n".format(balance, sym)) # write new content at the beginning
        for line in lines: # write old content after new
            f.write(line)
        f.close()
        print("successful trade, {} {} is the new balance.".format(balance, sym))
        
def buy_order(client, asset_sym, asset_balance, target_balance, last_closing_price):
    #sell order if our asset is ETH
    if (asset_sym == "ETH"):
        client.order_limit_sell(symbol= "ETHBTC", timeInForce = "GTC", quantity=round(float(asset_balance) - 0.001, 3), price=str(last_closing_price))
    #buy order if our asset is BTC
    else:
        print(round(float(target_balance) - 0.001, 4))
        client.order_limit_buy(symbol= "ETHBTC", timeInForce = "GTC", quantity=round(float(target_balance) - 0.001, 3), price=str(last_closing_price))
    print("order is place.")
        
def confirm_order(client):
    confirm = False
    while not confirm:
        order = client.get_open_orders(symbol = "ETHBTC")
        if not order:
            confirm = True
    print("order is confirmed")

def main():
    api_secret = ""
    api_key = ""
    
    print("program started")
    client = Client(api_key, api_secret, {"timeout": 100})
    
    
    while True:
        
        # get balance and target
        f= open("HISTORY.txt")
        contents = f.readlines()
        f.close()    
        asset_sym = contents[0].split()[1]
        target_sym = contents[1].split()[1]  
        asset_balance = float(contents[0].split()[0]) #asset_balance = float(client.get_asset_balance(asset = asset_sym)['free'])
        target_balance = float(target_profit())
        
        try:
            # fetch 1 minute klines for the last day up until now
            klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_1MINUTE, "1 min ago")
            most_recent = klines.pop()
            last_closing_price = float(most_recent[4])
	    # check buy/sell condition
            trade_condition_sastified = target_price_met(asset_sym, asset_balance, target_balance, last_closing_price)
            if (trade_condition_sastified):
                print("trading price met")
                buy_order(client, asset_sym, asset_balance, target_balance, last_closing_price)
                confirm_order(client)
                sleep(5)
		#edit history
                new_balance = float(client.get_asset_balance(asset = target_sym)['free'])
                edit_history(new_balance, target_sym)
		
	    # check price every 30s
            sleep(30)		
	    
        except BinanceAPIException as e:
            print(e.status_code)
            print(e.message)
            
if  __name__ =='__main__':main()