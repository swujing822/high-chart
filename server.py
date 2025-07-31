import tornado.ioloop
import tornado.web
import os
import pandas as pd
import json
import ccxt

DATA_DIR = './csv_orderbooks_symbol_20250730_100021_50_100'

import os
import json
import tornado.web

GLOBAL_JSON_PATH ='symbols_choosen.json'

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)

class UploadJsonHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            # 获取前端传来的 JSON 数据
            new_data = json.loads(self.request.body.decode('utf-8'))

            # 尝试读取现有数据，如果没有则初始化为空列表
            if os.path.exists(GLOBAL_JSON_PATH):
                with open(GLOBAL_JSON_PATH, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            else:
                existing_data = []

            # 追加新数据
            existing_data.append(new_data)

            # 保存回全局 JSON 文件
            with open(GLOBAL_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)

            self.write({'status': 'success', 'message': '数据已追加', 'total': len(existing_data)})
        except Exception as e:
            self.set_status(400)
            self.write({'status': 'error', 'message': str(e)})

    def get(self):
        # 返回当前的全局 JSON 内容
        if os.path.exists(GLOBAL_JSON_PATH):
            with open(GLOBAL_JSON_PATH, 'r', encoding='utf-8') as f:
                self.write(f.read())
        else:
            self.write(json.dumps([]))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class FileListHandler(tornado.web.RequestHandler):
    def get(self):
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
        self.write(json.dumps(files))


CSV_CACHE = {}  # filename -> (last_modified_time, DataFrame)

class DataHandler(tornado.web.RequestHandler):
    def get(self):
        filename = self.get_argument("file", "")
        start = int(self.get_argument("start", "0"))
        end = int(self.get_argument("end", "3000"))

        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.isfile(filepath):
            self.set_status(404)
            self.write("File not found")
            return

        # 检查缓存是否存在且没有被更新
        mtime = os.path.getmtime(filepath)
        cached = CSV_CACHE.get(filename)

        if cached and cached[0] == mtime:
            print("read from cached: key=", filename, cached[0])
            df = cached[1]
        else:
            try:
                df = pd.read_csv(filepath)
                CSV_CACHE[filename] = (mtime, df)
                print(f"[CACHE] Loaded file: {filename}, rows: {df.shape[0]}")
            except Exception as e:
                self.set_status(500)
                self.write(f"Error reading file: {str(e)}")
                return

        total_rows = df.shape[0]
        start = max(0, start)
        end = min(end, total_rows)
        if start >= end:
            self.set_status(400)
            self.write("Invalid range")
            return

        sliced_df = df.iloc[start:end]

        print(sliced_df.head())

        data = sliced_df.to_dict(orient="records")
        self.write(json.dumps(data))
        # print(sliced_df.shape)
        # self.write(json.dumps({
        #     sliced_df.to_dict(orient="records")
        # }))

class DynamicPageHandler(tornado.web.RequestHandler):
    def get(self, page_name):
        template_file = f"{page_name}.html"
        template_path = self.application.settings["template_path"]
        full_path = os.path.join(template_path, template_file)

        if os.path.exists(full_path):
            self.render(template_file)
        else:
            self.set_status(404)
            self.write(f"Page '{template_file}' not found.")

import tornado.web
import ccxt.async_support as ccxt
import json

class KlineHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Content-Type", "application/json")

    async def get(self):
        exchange_id = self.get_argument("exchange", "binance")
        symbol = self.get_argument("symbol", "BTC/USDT")
        timeframe = self.get_argument("timeframe", "1m")
        limit = int(self.get_argument("limit", "100"))
        since = self.get_argument("since", None)
        use_contract = self.get_argument("contract", "false").lower() == "true"

        print(exchange_id, symbol, timeframe, limit, use_contract)

        try:
            exchange_class = getattr(ccxt, exchange_id)
            exchange = exchange_class({'enableRateLimit': True})
            await exchange.load_markets()

            # 如果是合约，尝试找匹配的合约symbol
            if use_contract:
                matched = None
                for s in exchange.symbols:
                    # 这里简单匹配 startswith 且包含冒号，适应合约命名如 BTC/USDT:USDT 或 BTC/USDT:210625
                    if s.startswith(symbol) and ":" in s:
                        matched = s
                        break
                if matched:
                    symbol = matched

            if symbol not in exchange.symbols:
                self.write(json.dumps({"error": "Symbol not found on exchange"}))
                await exchange.close()
                return

            since_ms = int(since) if since else None
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since_ms, limit=limit)
            await exchange.close()

            result = [{"time": o[0], "close": o[4]} for o in ohlcv]
            self.write(json.dumps(result))
        except Exception as e:
            self.write(json.dumps({"error": str(e)}))


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/data", DataHandler),
        (r"/files", FileListHandler),
        (r"/klines", KlineHandler),
        (r"/upload_json", UploadJsonHandler),
        (r"/([a-zA-Z0-9_]+)", DynamicPageHandler),  # 捕获路径中的 a、b 等
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ],
    template_path="templates")

if __name__ == "__main__":
    make_app().listen(8080)
    print("🚀 Server running on http://localhost:8080")
    tornado.ioloop.IOLoop.current().start()
