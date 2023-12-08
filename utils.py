import json
from time import time
from config import api_key, api_secret
import requests

from cryptography.hazmat.primitives.asymmetric import ed25519
import base64


def sign_sig(data):
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(base64.b64decode(api_secret))
    signature = private_key.sign(data.encode())
    encoded_signature = base64.b64encode(signature).decode()
    return encoded_signature


def generate_request_params(msg=None, price=None, side=None, symbol=None, amount=None):
    now_time = int(time() * 1000)
    receive_window = 5000
    if msg == 'balance':
        sig = sign_sig(f'instruction=balanceQuery&timestamp={now_time}&window={receive_window}')
    elif msg == 'place_order':
        receive_window = 60000
        data = f'instruction=orderExecute&orderType=Limit&price={price}&quantity={amount}&side={side}&symbol={symbol}&timeInForce=IOC&timestamp={now_time}&window={receive_window}'
        sig = sign_sig(data)

    else:
        sig = sign_sig(msg)
    headers = {
        'X-Timestamp': str(now_time),
        'X-Window': str(receive_window),
        'X-API-Key': api_key,
        'X-Signature': sig,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    return headers


def get_ticker(symbol):
    msg = json.dumps({'symbol': symbol})
    headers = generate_request_params(msg)
    url = 'https://api.backpack.exchange/api/v1/ticker'
    res = requests.get(url, headers=headers, params={'symbol': 'SOL_USDC'})
    return res.json()


def get_market():
    url = 'https://api.backpack.exchange/api/v1/markets'
    headers = generate_request_params()
    res = requests.get(url, headers=headers)
    return res.json()


def get_order_book_depth(symbol):
    url = 'https://api.backpack.exchange/api/v1/depth'
    return requests.get(url, params={'symbol': symbol}).json()


def place_sell_order(symbol, side, price):
    url = 'https://api.backpack.exchange/api/v1/order'
    usdc_balance, sol_balance = get_balance()
    if side == 'Bid':
        sol_balance = usdc_balance / price * 0.9
    sol_balance = int(sol_balance * 100) / 100
    headers = generate_request_params('place_order', price, side, symbol, sol_balance)
    requests.post(url, headers=headers,
                  json={"side": side, "symbol": "SOL_USDC", "orderType": "Limit", "timeInForce": "IOC",
                        "quantity": f"{sol_balance}", "price": f"{price}"})


def get_balance():
    url = 'https://api.backpack.exchange/api/v1/capital'
    headers = generate_request_params('balance')
    res = requests.get(url, headers=headers).json()
    usdc_balance = res['USDC']['available']
    sol_balance = res['SOL']['available']
    # pyth_balance = res['PYTH']['available']
    return float(usdc_balance), float(sol_balance)


if __name__ == '__main__':
    # get_ticker('SOL_USDC')
    # 获取市场信息
    # market_info = get_market()
    # for i in market_info:
    #     print(i)
    # 获取代币深度
    # res = get_order_book_depth('SOL_USDC')
    # print(res)
    # 获取账户余额
    # get_balance()
    # 下单
    place_sell_order('SOL_USDC', 'Ask', 64.5)
