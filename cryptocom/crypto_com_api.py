import hmac
import hashlib
import json
import requests
import time
from time import sleep

API_KEY = ""
SECRET_KEY = ""


def getSign(request):
  """
  Given a request, create a digital signature and append it to the request.
  The dital signature should be stored in request["sig"].

  params: request: data request dict to make a call to private method
  returns: request: data request with the required "sig" field.

  """

  # First ensure the params are alphabetically sorted by key
  paramString = ""

  if "params" in request:
    for key in request['params']:
      paramString += key
      paramString += str(request['params'][key])

  sigPayload = request['method'] + str(request['id']) + request['api_key'] + paramString + str(request['nonce'])

  request['sig'] = hmac.new(
    bytes(str(SECRET_KEY), 'utf-8'),
    msg=bytes(sigPayload, 'utf-8'),
    digestmod=hashlib.sha256
  ).hexdigest()

  return request

def getPrice(symbol):
  """
  Given a symbol of a pair, make a call to crypto.com api to get the 
  current price of that pair

  params: symbol: string pair symbol
  returns: price: tuple, (ask, bid) price of the pair.
  """
  request = "https://api.crypto.com/v2/public/get-ticker?instrument_name="
  request += symbol

  response = requests.get(request)
  data = response.json()
  return (data["result"]["data"]["b"], data["result"]["data"]["k"])

def create_buy_order(symbol, price, quantity):
  """
  Given the symbol, price and quantity, make a buy order. Return the
  confirmation of the request.

  params: symbol: string pair symbol
          price: price to buy
          quantity: quantity to buy
  returns: response
  """
  request = {
    "id": 11,
    "api_key": API_KEY,
    "method": "private/create-order",
    "params": {
      "instrument_name": symbol,
      "price": price,
      "quantity": quantity,
      "side": "BUY",
      "type": "LIMIT",
    },
    "nonce": int(time.time() * 1000)
  }

  response = requests.post("https://api.crypto.com/v2/private/create-order", json=getSign(request))
  return response.json()

def create_sell_order(symbol, price, quantity):
  """
  Given the symbol, price and quantity, make a sell order. Return the
  confirmation of the request.

  params: symbol: string pair symbol
          price: price to buy
          quantity: quantity to buy
  returns: response
  """
  request = {
    "id": 11,
    "api_key": API_KEY,
    "method": "private/create-order",
    "params": {
      "instrument_name": "CRO_USDT",
      "price": price,
      "quantity": quantity,
      "side": "SELL",
      "type": "LIMIT",
    },
    "nonce": int(time.time() * 1000)
  }
  response = requests.post("https://api.crypto.com/v2/private/create-order", json=getSign(request))
  return response.json()

def get_balance(currency):
  request = {
    "id": 11,
    "api_key": API_KEY,
    "method": "private/get-account-summary",
    "params": {
        "currency": currency
    },
    "nonce": int(time.time() * 1000)
  }
  response = requests.post("https://api.crypto.com/v2/private/get-account-summary", json=getSign(request))
  data = response.json()
  # round to 3 decimal places
  return (float("{:.3f}".format(data["result"]["accounts"][0]["available"] - 0.001)))

def open_order():
  """
  find whether or not there is an open order
  """
  request = {
    "id": 12,
    "api_key": API_KEY,
    "method": "private/get-open-orders",
    "params": {
        "instrument_name": "CRO_USDT",
        "page": 0,
        "page_size": 2
    },
    "nonce": int(time.time() * 1000)
  }
  response = requests.post("https://api.crypto.com/v2/private/get-open-orders", json=getSign(request))
  data = response.json()
  return data["result"]["count"] != 0

def cancel_order():
  """
  cancel all open orders
  """
  request = {
    "id": 12,
    "api_key": API_KEY,
    "method": "private/cancel-all-orders",
    "params": {
         "instrument_name": "CRO_USDT"
    },
    "nonce": int(time.time() * 1000)
  }
  response = requests.post("https://api.crypto.com/v2/private/cancel-all-orders", json=getSign(request))
  data = response.json()
  print("order cancel: status: " + str(data["code"]))
  return (data["code"] == 0)

def transactionAlgo(transactions_number):
  """
  used to quickly satisfy the transaction requirement in API contest
  only 1 cro for each transaction make the fee neglegible.

  params: transactions_number: integer representing the number of unique transaction
  """
  count = 0
  while count < transactions_number:
    (people_buy_price, people_sell_price) = getPrice("CRO_USDT")
    if (get_balance("CRO") >= 1):
      create_sell_order("CRO_USDT", people_buy_price, 1)
      count += 1
      print(str(count) + "trades")
    elif (get_balance("USDT") >= 0.2):
      create_buy_order("CRO_USDT", people_sell_price, 1)
      count += 1
      print(str(count) + "trades")
    # make a trade every second
    sleep(1)

def volumnAlgo(transactions_number):
  """
  used to satisfy the volumn requirement in API contest.
  make limit order a bit higher/lower than market price to try and offset
  the opportunity risk and fees.

  params: transactions_number: integer representing the number of unique transaction
                  that is needed to sastify the volume

  """
  count = 1

  while count < transactions_number:
    # if order have not fill after 30 minutes, find the new price
    # and cancel old order because price might've shifted
    cancel_order()
    count -= 1
    (people_buy_price, people_sell_price) = getPrice("CRO_USDT")
    #wierd bug where adding then subtracting float mess up precision
    people_buy_price = float("{:.4f}".format(people_buy_price + 0.0003))
    people_sell_price = float("{:.4f}".format(people_sell_price - 0.0003))
    time_end = time.time() + 60 * 30

    while time.time() < time_end:
      # wait until order is filled
      if(not open_order()):
        cro_balance = get_balance("CRO")
        usdt_balance = get_balance("USDT")
        if (cro_balance >= 500):
          print(create_sell_order("CRO_USDT", people_buy_price, cro_balance))
          count += 1
          print("made sell order, total: " + str(count) + "trades")
          #reset timer
          time_end = time.time() + 60 * 30
          sleep(2)
        elif (usdt_balance >= 100):
          cro_amount = float("{:.3f}".format((usdt_balance/people_sell_price) - 0.001))
          print(create_buy_order("CRO_USDT", people_sell_price, cro_amount))
          count += 1
          print("made buy order, total: "+ str(count) + "trades")
          #reset timer
          time_end = time.time() + 60 * 30
          sleep(2)
      #check every 5s
      sleep(5)


def main():
  #transactionAlgo(1000)

  #100 transaction for $100 000 volumn if used $1000 per trade
  volumnAlgo(100)
if  __name__ =='__main__':main()
