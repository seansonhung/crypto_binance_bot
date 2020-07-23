# crypto_binance_bot
A terminal crypto trading bot on binance exchange. The trading method is simple, trading back and forth between 2 coins and always end up with more coins in theory. This method works well if the price of the trading pair are relatively stable and you wouldn't mind holding one coin or another. A flaw with this method is that if the price of trading pair shift from where you started, it might mean you will end up holding a different type of coin than what you started with. This also mean there is a risk that the dollar value of your coins might be lower than of the coins you started with.

# Strategy

Ex: assume 1 BTC = 1 ETH and we want to end up with 2% more coins each cycle of trade. Preferrable > 0.2% since binance have a 0.1% fee per trade.

Start with 1 ETH.
Trade to BTC when ETHBTC price is (1.01) we get 1.01 BTC
Trade to ETH when ETHBTC price is (~0.9902) we get  1.02 ETH
Repeat

# How to run the bot

import the python-binance package:
for python 2.x run the command `pip install python-binance`
for python 3.x run the command `pip3 install python-binance`

run the python file:
for python 2.x run the command `python crypto_bot.py`
for python 3.x run the command `python crypto_bot.py`

follow the steps in the terminal for required inputs. 


# crypto.com_api_trading_bot
A bot used to enter crypto.com api trading events (v2).

There are two methods used to satisfy the minimum requirements.
1) Trade 1 CRO back and forth to get the 1000 unique transaction requirement. The fee is very low due to the small transaction.
2) Trade USDT back and forth at maker price a little above market price to offset the opportunity risks and fees.
