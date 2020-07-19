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

def target_profit(history_file, percent_profit):
    # percent_profit % increased in amount of coin after 2 transactions, before fees
    # inital balance is from historical data, 1 transaction ago.
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
    
def get_syms_and_balance(history_file, percent_profit):
    # get balance and target
    f= open(history_file)
    contents = f.readlines()
    f.close()    
    asset_sym = contents[0].split()[1]
    target_sym = contents[1].split()[1]  
    asset_balance = float(contents[0].split()[0]) #asset_balance = float(client.get_asset_balance(asset = asset_sym)['free'])
    target_balance = float(target_profit(history_file, percent_profit))   
    return(asset_sym, target_sym, asset_balance, target_balance)

def new_session_history_file(history_file, asset_sym, amount, target_sym, target_amount):
    #write into file
    f = open(history_file,'r+')
    contents = f.read().split("\n")
    f.seek(0)
    f.truncate()
    f.write("{} {} \n".format(amount, asset_sym))
    f.write("{} {} \n".format(target_amount, target_sym)) # write new content at the beginning
    f.close()

def ETHBTC_bot(client, asset_sym, amount, percent_profit):
    pair_sym = "ETHBTC"
    last_closing_price = get_closing_price(client, pair_sym)
    history_file = "ETHBTC_HISTORY.txt"
    target_sym = None
    target_amount = None
    if (asset_sym == "ETH"):
        target_sym = "BTC"
        target_amount = (amount * last_closing_price)
    else:
        target_sym = "ETH"
        target_amount = (amount / last_closing_price)
    # get 1st target amount
    # start a new session, delete content of history file and start with initial amount
    new_session_history_file(history_file, asset_sym, amount * (1 + percent_profit/2), target_sym, target_amount)

    while True:
        # get balance and target
        (asset_sym, target_sym, asset_balance, target_balance) = get_syms_and_balance(history_file, percent_profit)
        try:
            last_closing_price = get_closing_price(client, pair_sym)
            # check buy/sell condition
            trade_condition_sastified = target_price_met(asset_sym, amount, target_balance, last_closing_price, pair_sym)
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
                edit_history(history_file, new_balance, target_sym)

        except BinanceAPIException as e:
            print(e.status_code)
            print(e.message)
        sleep(30)

def XRPBTC_bot(client, asset_sym, amount, percent_profit):
    pair_sym = "XRPBTC"
    last_closing_price = get_closing_price(client, pair_sym)
    history_file = "XRPBTC_HISTORY.txt"
    target_sym = None
    target_amount = None
    if (asset_sym == "XRP"):
        target_sym = "BTC"
        target_amount = (amount * last_closing_price)
    else:
        target_sym = "XRP"
        target_amount = (amount / last_closing_price)
    # get 1st target amount
    # start a new session, delete content of history file and start with initial amount
    new_session_history_file(history_file, asset_sym, amount * (1 + percent_profit/2), target_sym, target_amount)

    while True:
        # get balance and target
        (asset_sym, target_sym, asset_balance, target_balance) = get_syms_and_balance("XRPBTC_HISTORY.txt", percent_profit)
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
        sleep(30)

def check_balance(client):
    # get the asset balance of the 3 coin supported by this bot
    eth = float(client.get_asset_balance(asset = 'ETH')['free'])
    btc = float(client.get_asset_balance(asset = 'BTC')['free'])
    xrp = float(client.get_asset_balance(asset = 'XRP')['free'])
    print("Your balance is: "+ str(eth) + " ETH "+ str(btc) + " BTC "+ str(xrp) + " XRP. \n")

def check_coin_available(client, asset, amount):
    # return whether the amount of coin wanted to be trade is actually available in balance
    balance = float(client.get_asset_balance(asset = asset)['free'])
    return (balance >= amount)


def main():
    client = None
    #get the user api keys and check balance
    while True:
        try:
            api_secret = input("Enter your binance api secret: ")
            api_key = input("Enter your binance api key: ")

            client = Client(api_key, api_secret, {"timeout": 100})
            #test to see if client is valid
            eth = float(client.get_asset_balance(asset = 'ETH')['free'])
            break
        except:
            print("api secret and/or api key does not match existing user")
	
    print("Successfully logged into your binance account.")

    while True:
        option = input("enter '1' to check your balance. \n" +
                        "enter '2' to start trading ETHBTC pair. \n" +
                        "enter '3' to start trading XRPBTC pair. \n" +
                        "enter 'exit' to exit. \n")
        # checking account balance
        if (option == "1"):
            check_balance(client)
        # ETHBTC trading pair
        elif (option == "2"):
            while True:
                option2 = input("enter the starting coin and amount and the percent increase per cycle (ex: ETH 1.0 2) to continue or\n" +
                                "enter '2' to go back \n" +
                                "enter 'exit' to exit \n")
                if (option2 == "2"):
                    break
                elif(option2 =="exit"):
                    exit()
                else:
                    starting_coin_amount = option2.split(" ")
                    if (len(starting_coin_amount) != 3):
                        print("invalid input")
                    elif (starting_coin_amount[0] != "ETH" and starting_coin_amount[0] != "BTC"):
                        print("only support ETH or BTC")
                    elif (not check_coin_available(client, starting_coin_amount[0], float(starting_coin_amount[1]))):
                        print("trading amount cannot be larger than account balance")
                    elif (float(starting_coin_amount[2]) < 0.2):
                        print("trading percent increase should be > 0.2% to offset binance trading fees")
                    else:
                        ETHBTC_bot(client, starting_coin_amount[0], float(starting_coin_amount[1]), float(starting_coin_amount[2])/100)
                        
        # XRPBTC trading pair
        elif (option == "3"):
            while True:
                option2 = input("enter the starting coin and amount and the percent increase per cycle (ex: XRP 1.0 2 or BTC 1.0 3) to continue or\n" +
                                "enter '2' to go back \n" +
                                "enter 'exit' to exit \n")
                if (option2 == "2"):
                    break
                elif(option2 =="exit"):
                    exit()
                else:
                    starting_coin_amount = option2.split(" ")
                    if (len(starting_coin_amount) != 3):
                        print("invalid input")
                    elif (starting_coin_amount[0] != "XRP" and starting_coin_amount[0] != "BTC"):
                        print("only support XRP or BTC")
                    elif (not check_coin_available(client, starting_coin_amount[0], float(starting_coin_amount[1]))):
                        print("trading amount cannot be larger than account balance")
                    elif (float(starting_coin_amount[2]) < 0.2):
                        print("trading percent increase should be > 0.2% to offset binance trading fees")
                    else:
                        XRPBTC_bot(client, starting_coin_amount[0], float(starting_coin_amount[1]), float(starting_coin_amount[2])/100)

        #exit
        elif (option == "exit"):
            exit()
        else:
            print("Not a valid option \n") 

if  __name__ =='__main__':main()