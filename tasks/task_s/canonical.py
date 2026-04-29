"""
Task-S canonical reference implementation — 단축 URL 서비스
목적: hidden_tests.py sanity check용. 모든 hidden test를 통과해야 함.
실행: python tasks/task_s/canonical.py
의존성: stdlib only
"""
import hashlib
import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

_url_to_code: dict[str, str] = {}
_code_to_url: dict[str, str] = {}
_HTTP_RE = re.compile(r"^https?://")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/shorten":
            self._respond(404, {"detail": "Not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, ValueError):
            self._respond(400, {"detail": "Invalid JSON"})
            return
        orig = body.get("url", "")
        if not orig or not _HTTP_RE.match(orig):
            self._respond(400, {"detail": "Invalid URL: must start with http:// or https://"})
            return
        if orig in _url_to_code:
            self._respond(201, {"code": _url_to_code[orig]})
            return
        code = hashlib.sha256(orig.encode()).hexdigest()[:7]
        _url_to_code[orig] = code
        _code_to_url[code] = orig
        self._respond(201, {"code": code})

    def do_GET(self):
        code = self.path.lstrip("/")
        if code in _code_to_url:
            self.send_response(302)
            self.send_header("Location", _code_to_url[code])
            self.end_headers()
        else:
            self._respond(404, {"detail": "Code not found"})

    def _respond(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_) -> None:
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving on http://0.0.0.0:{port}")
    server.serve_forever()
