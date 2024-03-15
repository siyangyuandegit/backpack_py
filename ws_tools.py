import asyncio
import random
import time

import requests
import socks
import websockets
import json
from utils import place_sell_order, get_balance, get_deposit_addr
import socket
from config import backpack_user_info

sol_bid = 0
sol_ask = 0


async def subscribe_to_stream(api_key, api_secret):
    global sol_ask, sol_bid
    # uri = "wss://ws.backpack.exchange/stream"
    uri = "wss://ws.backpack.exchange/"
    retry_count = 0
    while retry_count < 100:
        try:
            async with websockets.connect(uri) as websocket:
                subscribe_message = {
                    "method": "SUBSCRIBE",
                    "params": ["bookTicker.SOL_USDC"]
                }

                await websocket.send(json.dumps(subscribe_message))
                count = 0
                while count < 1000:
                    response = json.loads(await websocket.recv())['data']
                    # print(response)
                    sol_ask = float(response['a'])
                    ask_amount = float(response['A'])
                    sol_bid = float(response['b'])
                    bid_amount = float(response['B'])
                    # print(f'当前sol买一价: {sol_bid}, 数量: {bid_amount}, 卖一价: {sol_ask}, 数量: {ask_amount}')
                    rand_num = random.randint(1, 800)

                    if rand_num < 2:
                        print(f'下单下单, 当前时间: {time.time()}')
                        print(f'当前sol买一价: {sol_bid}, 数量: {bid_amount}, 卖一价: {sol_ask}, 数量: {ask_amount}')

                        if sol_ask > 0:
                            await place_sell_order('SOL_USDC', 'Bid', float(format(sol_ask + 0.02, '.2f')), api_key, api_secret)
                            await place_sell_order('SOL_USDC', 'Ask', float(format(sol_bid - 0.02, '.2f')), api_key, api_secret)
                            count += 1
                    else:
                        # print('控制频率，放弃下单')
                        pass
                break
        except Exception as e:
            retry_count += 1
            await asyncio.sleep(2)
            print(e)


async def test():
    await asyncio.sleep(10)
    print(f'完成操作')


async def main():
    for user_name, user_info in backpack_user_info.items():
        # print(user_name, user_info)
        if user_name == 'gxl':
            print(requests.get('https://ipinfo.io/').json())
            print(f'开始{user_name}刷量')
            deposit_addr = await get_deposit_addr(user_info['api_key'], user_info['api_secret'], 'Solana')
            while True:
                usdc_balance, sol_balance = await get_balance(user_info['api_key'], user_info['api_secret'])
                if usdc_balance > 0 or sol_balance > 0:
                    break
                print(f'等待充值中, Solana Deposit Address: {deposit_addr}')
                await asyncio.sleep(5)

            await subscribe_to_stream(user_info['api_key'], user_info['api_secret'])

        if user_name != 'lwb':
            pass
        else:
            # print(user_info)
            socks.setdefaultproxy(socks.SOCKS5, user_info['proxy_host'], user_info['proxy_port'],
                                  username=user_info['proxy_username'], password=user_info['proxy_password'])
            print(socks.get_default_proxy())
            socket.socket = socks.socksocket
            print(requests.get('https://ipinfo.io/').json())
            print(f'开始{user_name}刷量')
            await subscribe_to_stream(user_info['api_key'], user_info['api_secret'])
            print(f'{user_name}刷量完成')
        # 运行 WebSocket 客户端
        # asyncio.get_event_loop().run_until_complete(subscribe_to_stream(user_info['api_key'], user_info['api_secret']))


if __name__ == '__main__':
    asyncio.run(main())
