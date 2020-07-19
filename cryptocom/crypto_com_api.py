import hmac
import hashlib
import json
import requests
import time

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


def main():
  #resp = requests.get("https://api.crypto.com/v2/public/get-trades")
  # request = {
  #   "id": 11,
  #   "api_key": API_KEY,
  #   "method": "private/get-account-summary",
  #   "params": {
  #       "currency": "CRO"
  #   },
  #   "nonce": int(time.time() * 1000)
  # }
  # resp = requests.post("https://api.crypto.com/v2/private/get-account-summary", json=getSign(request))
  # code = json.dumps(resp.json())
  # print(code)
  (bid_price, ask_price) = getPrice("CRO_USDT")
  print(bid_price)

if  __name__ =='__main__':main()
