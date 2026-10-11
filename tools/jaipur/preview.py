"""Quiet static preview server, with room for parallel browser asset requests."""
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

ThreadingHTTPServer.request_queue_size = 128
root = Path(__file__).resolve().parents[2] / 'rawcoderz' / 'jaipur'
print('Local: http://127.0.0.1:8766/', flush=True)
ThreadingHTTPServer(('127.0.0.1',8766),partial(Handler,directory=str(root))).serve_forever()
