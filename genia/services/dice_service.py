import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from genia.interpreter import GENIAInterpreter

SCRIPT_PATH = Path(__file__).resolve().parents[2] / 'scripts' / 'dice.genia'
BASE_CODE = SCRIPT_PATH.read_text()

def dict_get(d, key, default=None):
    return d.get(key, default)

def _load_interpreter():
    interp = GENIAInterpreter()
    interp.run(BASE_CODE, args=[])
    return interp

def roll(count: int, sides: int) -> int:
    """Roll `count` dice each with `sides` sides and return the sum."""
    interp = _load_interpreter()
    func = interp.interpreter.functions["roll"]
    return interp.interpreter.call_function(func, [count, sides], (0, 0))

def handle_request(body: str) -> str:
    interp = _load_interpreter()
    func = interp.interpreter.functions["handle_request"]
    return interp.interpreter.call_function(func, [body], (0, 0))


class DiceRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            response = handle_request(body)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        except Exception as exc:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(exc)}).encode('utf-8'))


def serve(host: str = '127.0.0.1', port: int = 8000):
    """Start a simple HTTP server for rolling dice."""
    server = HTTPServer((host, port), DiceRequestHandler)
    print(f"Serving dice roll service on http://{host}:{port}")
    server.serve_forever()


if __name__ == '__main__':
    serve()
