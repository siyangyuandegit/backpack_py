import asyncio
import json
from time import time
from config import backpack_user_info
import requests

from cryptography.hazmat.primitives.asymmetric import ed25519
import base64

import aiohttp


async def balance_coin_value(symbol, bid_price, ask_price, api_key, api_secret):
    """

    :param symbol:
    :param bid_price: 当前买一
    :param ask_price: 当前卖一
    :param api_key:
    :param api_secret:
    :return:
    """
    url = 'https://api.backpack.exchange/api/v1/order'

    # 暂定千三


async def place_order(symbol, side, coin_amt, price, api_key, api_secret):
    url = 'https://api.backpack.exchange/api/v1/order'
    headers = await generate_request_params('place_order', price, side, symbol, coin_amt, api_key=api_key,
                                            api_secret=api_secret)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers,
                                json={"side": side, "symbol": "SOL_USDC", "orderType": "Limit", "timeInForce": "IOC",
                                      "quantity": f"{coin_amt}", "price": f"{price}"}) as resp:
            response = await resp.text()
            print(response)


async def sign_sig(data, api_secret):
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(base64.b64decode(api_secret))
    signature = private_key.sign(data.encode())
    encoded_signature = base64.b64encode(signature).decode()
    return encoded_signature


async def generate_request_params(msg=None, price=None, side=None, symbol=None, amount=None, chain=None, api_key='',
                                  api_secret=''):
    now_time = int(time() * 1000)
    receive_window = 5000
    if msg == 'balance':
        sig = await sign_sig(f'instruction=balanceQuery&timestamp={now_time}&window={receive_window}', api_secret)
    elif msg == 'place_order':
        receive_window = 60000
        data = f'instruction=orderExecute&orderType=Limit&price={price}&quantity={amount}&side={side}&symbol={symbol}&timeInForce=IOC&timestamp={now_time}&window={receive_window}'
        # data = f'instruction=orderExecute&orderType=Market&quoteQuantity={amount}&side={side}&symbol={symbol}&timeInForce=IOC&timestamp={now_time}&window={receive_window}'
        sig = await sign_sig(data, api_secret)
    elif msg == 'deposit_addr':
        sig = await sign_sig(
            f'instruction=depositAddressQuery&blockchain={chain}&timestamp={now_time}&window={receive_window}',
            api_secret)
    elif msg == 'volume':
        sig = await  sign_sig(
            f'instruction=quoteVolume&blockchain={chain}&timestamp={now_time}&window={receive_window}',
            api_secret
        )
    else:
        sig = await sign_sig(msg, api_secret)
    headers = {
        'X-Timestamp': str(now_time),
        'X-Window': str(receive_window),
        'X-API-Key': api_key,
        'X-Signature': sig,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    return headers


async def get_ticker(symbol, api_key):
    msg = json.dumps({'symbol': symbol})
    headers = await generate_request_params(msg, api_key=api_key)
    url = 'https://api.backpack.exchange/api/v1/ticker'
    res = requests.get(url, headers=headers, params={'symbol': 'SOL_USDC'})
    return res.json()


def get_market(api_key):
    url = 'https://api.backpack.exchange/api/v1/markets'
    headers = generate_request_params(api_key=api_key)
    res = requests.get(url, headers=headers)
    return res.json()


def get_order_book_depth(symbol):
    url = 'https://api.backpack.exchange/api/v1/depth'
    return requests.get(url, params={'symbol': symbol}).json()


async def get_usdc_balance(api_key, api_secret):
    url = 'https://api.backpack.exchange/api/v1/capital'
    headers = await generate_request_params('balance', api_key=api_key, api_secret=api_secret)

    # 使用aiohttp进行异步HTTP GET请求
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            # 确保响应状态码为200
            if response.status == 200:
                res = await response.json()  # 异步获取响应的JSON数据
                try:
                    usdc_balance = res['USDC']['available']
                    return float(usdc_balance)
                except Exception as e:
                    return 0.0
            else:
                print(f"Failed to get balance, status code: {response.status}")
                return 0.0


async def get_balance(api_key, api_secret):
    url = 'https://api.backpack.exchange/api/v1/capital'
    headers = await generate_request_params('balance', api_key=api_key, api_secret=api_secret)

    # 使用aiohttp进行异步HTTP GET请求
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            # 确保响应状态码为200
            if response.status == 200:
                res = await response.json()  # 异步获取响应的JSON数据
                try:
                    usdc_balance = res['USDC']['available']
                except Exception as e:
                    usdc_balance = 0
                try:
                    sol_balance = res['SOL']['available']
                except Exception as e:
                    sol_balance = 0
                    # pyth_balance = res['PYTH']['available']
                return float(usdc_balance), float(sol_balance)
            else:
                print(f"Failed to get balance, status code: {response.status}")
                return 0.0, 0.0


async def get_volume(api_key, api_secret):
    url = 'https://api.backpack.exchange/api/v1/capital'
    headers = await generate_request_params('volume', api_key=api_key, api_secret=api_secret)

    # 使用aiohttp进行异步HTTP GET请求
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            # 确保响应状态码为200
            if response.status == 200:
                res = await response.json()  # 异步获取响应的JSON数据
                try:
                    usdc_balance = res['USDC']['available']
                except Exception as e:
                    usdc_balance = 0
                try:
                    sol_balance = res['SOL']['available']
                except Exception as e:
                    sol_balance = 0
                    # pyth_balance = res['PYTH']['available']
                return float(usdc_balance), float(sol_balance)
            else:
                print(f"Failed to get balance, status code: {response.status}")
                return 0.0, 0.0


async def get_deposit_addr(api_key, api_secret, chain):
    url = 'https://api.backpack.exchange/wapi/v1/capital/deposit/address'
    headers = await generate_request_params('deposit_addr', api_key=api_key, api_secret=api_secret, chain=chain)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params={'blockchain': chain}) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/json' in content_type:
                        response_json = await response.json()
                        return response_json['address']
                    elif 'text/plain' in content_type:
                        response_text = await response.text()
                        return response_text
                    else:
                        # 处理其他类型的响应
                        response_content = await response.read()
                        return response_content
                else:
                    # 处理响应状态码不为200的情况
                    print(f"Error: {response.status}")
                    return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


async def main():
    ldp_api_key = backpack_user_info['ldp']['api_key']
    ldp_api_secret = backpack_user_info['ldp']['api_secret']
    print(ldp_api_secret)
    print(await get_balance(ldp_api_key, ldp_api_secret))
    addr = await get_deposit_addr(ldp_api_key, ldp_api_secret, 'Solana')
    print(addr)


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

    asyncio.run(main())
    # print(get_balance(ldp_api_key, ldp_api_secret))

    # 下单
    # place_order('SOL_USDC', 'Ask', 64.5)
