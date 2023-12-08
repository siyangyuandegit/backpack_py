import asyncio
import time

import websockets
import json
from utils import place_sell_order

sol_bid = 0
sol_ask = 0


async def subscribe_to_stream():
    global sol_ask, sol_bid
    uri = "wss://ws.backpack.exchange/stream"

    async with websockets.connect(uri) as websocket:
        # 构建订阅请求的 JSON 消息
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": ["SOL_USDC@bookTicker"]  # 替换为实际的流名称
        }

        # 发送订阅请求
        await websocket.send(json.dumps(subscribe_message))
        # 等待并打印服务器响应
        count = 0
        while count < 5:
            response = json.loads(await websocket.recv())['data']
            print(response)
            sol_ask = float(response['a'])
            ask_amount = float(response['A'])
            print(response['b'])
            sol_bid = float(response['b'])
            bid_amount = float(response['B'])
            print(f'当前sol买一价: {sol_bid}, 数量: {bid_amount}, 卖一价: {sol_ask}, 数量: {ask_amount}')
            if sol_ask > 0:
                place_sell_order('SOL_USDC', 'Ask', sol_bid)
                time.sleep(2)
                place_sell_order('SOL_USDC', 'Bid', sol_ask)
                count += 1


# 运行 WebSocket 客户端
asyncio.get_event_loop().run_until_complete(subscribe_to_stream())
