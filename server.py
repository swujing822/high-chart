import tornado.ioloop
import tornado.web
import os
import pandas as pd
import json

DATA_DIR = './csv_orderbooks_symbol'

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

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/data", DataHandler),
        (r"/files", FileListHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ],
    template_path="templates")

if __name__ == "__main__":
    make_app().listen(8080)
    print("🚀 Server running on http://localhost:8080")
    tornado.ioloop.IOLoop.current().start()
