import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from genia.interpreter import GENIAInterpreter

SCRIPT_PATH = Path(__file__).resolve().parents[2] / 'scripts' / 'dice.genia'
BASE_CODE = SCRIPT_PATH.read_text()

def roll(count: int, sides: int) -> int:
    """Roll `count` dice each with `sides` sides and return the sum."""
    interp = GENIAInterpreter()
    return interp.run(BASE_CODE, args=[str(count), str(sides)])


class DiceRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
            count = int(data.get('count', 1))
            sides = int(data.get('sides', 6))
            result = roll(count, sides)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'result': result}).encode('utf-8'))
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
