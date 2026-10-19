import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse

from .__main__ import ROOT,example
from .engine import generate,counterfactual


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*_):pass
    def reply(self,code,data,kind="application/json"):
        content=data if isinstance(data,bytes) else json.dumps(data,allow_nan=False).encode()
        self.send_response(code);self.send_header("Content-Type",kind+"; charset=utf-8");self.send_header("Content-Length",str(len(content)));self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff");self.end_headers();self.wfile.write(content)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/example":return self.reply(200,example())
        if path in ("/","/app.js","/style.css"):
            name="index.html" if path=="/" else path[1:];kind={"index.html":"text/html","app.js":"text/javascript","style.css":"text/css"}[name];return self.reply(200,(ROOT/"web"/name).read_bytes(),kind)
        self.reply(404,{"error":"not_found"})
    def do_POST(self):
        origin=self.headers.get("Origin")
        if origin and origin!=f"http://127.0.0.1:{self.server.server_port}":return self.reply(403,{"error":"origin_denied"})
        try:
            size=int(self.headers.get("Content-Length","0"))
            if not 0<size<=200000:raise ValueError("invalid_size")
            body=json.loads(self.rfile.read(size))
            if not isinstance(body,dict):raise ValueError("invalid_input")
            if self.path=="/api/generate":result=generate(body["spec"],body.get("seed",7),seconds=8)
            elif self.path=="/api/pair":result=counterfactual(body["spec"],body["row"],body["label"])
            else:return self.reply(404,{"error":"not_found"})
            self.reply(200,result)
        except (ValueError,TypeError,KeyError):self.reply(400,{"error":"invalid_input","messages":["Entrée non valide","Invalid input","Entrada no válida"]})


def serve(port=8767):ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()
