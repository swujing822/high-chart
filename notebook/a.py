import ccxt
import pandas as pd
import matplotlib.pyplot as plt

symbol_spot = 'BAL/USDT'            # 现货
symbol_future = 'BAL/USDT:USDT'     # 永续合约（USDT本位）

symbol_spot = 'BMEX/USDT'            # 现货
symbol_future = 'BMEX/USDT:USDT'     # 永续合约（USDT本位）

# bitmex     | BMEX/USDT:USDT

# 初始化交易所对象
# spot = ccxt.gateio()
# future = ccxt.gateio({
#     'options': {
#         'defaultType': 'future'
#     }
# })

spot = ccxt.bitmex()
future = ccxt.bitmex({
    'options': {
        'defaultType': 'future'
    }
})

# 加载市场
spot.load_markets()
future.load_markets()

# 确认 symbol 是否存在
if symbol_spot not in spot.markets:
    raise Exception("Spot symbol not found")
if symbol_future not in future.markets:
    raise Exception("Future symbol not found")

# 获取1m K线（限制 100 根）
ohlcv_spot = spot.fetch_ohlcv(symbol_spot, timeframe='1m', limit=100)
ohlcv_fut = future.fetch_ohlcv(symbol_future, timeframe='1m', limit=100)

# 转换为 DataFrame
df_spot = pd.DataFrame(ohlcv_spot, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df_fut = pd.DataFrame(ohlcv_fut, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# 时间戳转换
df_spot['datetime'] = pd.to_datetime(df_spot['timestamp'], unit='ms')
df_fut['datetime'] = pd.to_datetime(df_fut['timestamp'], unit='ms')

# 统一时间戳为索引，方便对齐
df_spot.set_index('datetime', inplace=True)
df_fut.set_index('datetime', inplace=True)

# 取收盘价
df = pd.DataFrame()
df['spot'] = df_spot['close']
df['future'] = df_fut['close']
df.dropna(inplace=True)

# 计算价差
df['spread'] = df['future'] - df['spot']

# 画图
plt.figure(figsize=(14, 8))

# 主图：现货 vs 合约
plt.subplot(2, 1, 1)
plt.plot(df.index, df['spot'], label='Spot Price (BAL/USDT)', color='blue')
plt.plot(df.index, df['future'], label='Futures Price (BAL/USDT:USDT)', color='orange')
plt.title('BAL/USDT Spot vs Futures Price')
plt.legend()
plt.grid(True)

# 副图：价差
plt.subplot(2, 1, 2)
plt.plot(df.index, df['spread'], label='Spread (Futures - Spot)', color='red')
plt.axhline(0, color='gray', linestyle='--')
plt.title('Price Spread')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
