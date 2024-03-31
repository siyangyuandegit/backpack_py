import asyncio
import random
import time

import requests
import socks
import websockets
import json
from utils import place_order, get_balance, get_deposit_addr, balance_coin_value
import socket
from config import backpack_user_info

# from config_labs import backpack_user_info

sol_bid = 0
sol_ask = 0


async def subscribe_to_stream(api_key, api_secret):
    global sol_ask, sol_bid
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
                while True:
                    response = json.loads(await websocket.recv())['data']
                    # print(response)
                    sol_ask = float(response['a'])
                    ask_amount = float(response['A'])
                    sol_bid = float(response['b'])
                    bid_amount = float(response['B'])
                    # print(f'当前sol买一价: {sol_bid}, 数量: {bid_amount}, 卖一价: {sol_ask}, 数量: {ask_amount}')
                    rand_num = random.randint(1, 1000)

                    if rand_num < 5:
                        # print(f'下单下单, 当前时间: {time.time()}')
                        print(f'当前sol买一价: {sol_bid}, 数量: {bid_amount}, 卖一价: {sol_ask}, 数量: {ask_amount}')

                        if sol_ask > 0:
                            usdc_balance, sol_balance = await get_balance(api_key, api_secret)
                            usdc_value = usdc_balance
                            sol_value = sol_balance * (sol_bid - 0.2)
                            print(f'当前sol: {sol_balance} 价值: {sol_value}, usdc: {usdc_balance},')
                            diff_ratio = abs(sol_value - usdc_value) / usdc_value
                            if diff_ratio > 0.003:
                                # 卖出
                                if sol_value > usdc_value:
                                    amount_to_sell = float(
                                        format((sol_value - usdc_value) / (sol_bid - 0.1) / 2, '.2f'))
                                    print(f'需要卖出sol: {amount_to_sell}')
                                    await place_order('SOL_USDC', 'Ask', amount_to_sell,
                                                      float(format(sol_bid - 0.04, '.2f')), api_key,
                                                      api_secret)

                                else:
                                    amount_to_buy = float(
                                        format((usdc_value - sol_value) / (sol_ask + 0.1) / 2, '.2f'))
                                    print(f'需要买入sol: {amount_to_buy}')

                                    await place_order('SOL_USDC', 'Bid', amount_to_buy,
                                                      float(format(sol_ask + 0.04, '.2f')), api_key,
                                                      api_secret)
                            count += 1
                    else:
                        # print('控制频率，放弃下单')
                        pass
                break
        except Exception as e:
            retry_count += 1
            await asyncio.sleep(2)
            print(e)


async def main():
    count = 0
    while count < 1:
        for user_name, user_info in backpack_user_info.items():
            socks.setdefaultproxy(socks.SOCKS5, user_info['proxy_host'], int(user_info['proxy_port']),
                                  username=user_info['proxy_username'], password=user_info['proxy_password'])
            socket.socket = socks.socksocket

            print(f'开始{user_name}刷量')
            deposit_addr = await get_deposit_addr(user_info['api_key'], user_info['api_secret'], 'Solana')
            while True:
                # usdc_balance = await get_usdc_balance(user_info['api_key'], user_info['api_secret'])
                usdc_balance, sol_balance = await get_balance(user_info['api_key'], user_info['api_secret'])

                if usdc_balance > 0:
                    break
                print(f'等待充值中, Solana Deposit Address: {deposit_addr}')
                await asyncio.sleep(5)
            print(f'用户资产: USDC: {usdc_balance}, sol: {sol_balance}')
            if usdc_balance < 10 and sol_balance < 0.1:
                print(f'用户: {user_name} 已经完任务，USDC余额: {usdc_balance}')
                continue
            # if sol_balance < 0.1:
            #     print(f'用户: {user_name} 已经完任务，USDC余额: {usdc_balance}')
            #     continue
            await subscribe_to_stream(user_info['api_key'], user_info['api_secret'])
        count += 1


if __name__ == '__main__':
    asyncio.run(main())
