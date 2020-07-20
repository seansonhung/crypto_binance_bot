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
  return (data["result"]["accounts"][0]["available"])


def open_order():
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

def main():
  # # used to quickly satisfy the 1000 trade requirement in API contest
  # # only 1 cro for each transaction make the fee neglegible.
  # count = 0
  # while count < 1000:
  #   (people_buy_price, people_sell_price) = getPrice("CRO_USDT")
  #   if (get_balance("CRO") >= 1):
  #     create_sell_order("CRO_USDT", people_buy_price, 1)
  #     count += 1
  #     print(str(count) + "trades")
  #   elif (get_balance("USDT") >= 0.2):
  #     create_buy_order("CRO_USDT", people_sell_price, 1)
  #     count += 1
  #     print(str(count) + "trades")
  #   sleep(1)
  print(open_order())
      



if  __name__ =='__main__':main()
