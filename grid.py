def initialize_grid_orders(lower_bound, upper_bound, grid_number, total_amount):
    grid_size = (upper_bound - lower_bound) / grid_number
    amount_per_order = total_amount / grid_number

    grid_orders = []

    # 创建买单
    for i in range(grid_number // 2):
        price = lower_bound + i * grid_size
        grid_orders.append({'price': round(price, 2), 'amount': amount_per_order, 'type': 'buy'})

    # 创建卖单
    for i in range(grid_number // 2, grid_number):
        price = lower_bound + i * grid_size
        grid_orders.append({'price': round(price, 2), 'amount': amount_per_order, 'type': 'sell'})

    return grid_orders

