import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from src.agents.pipeline import analyze_event
from src.agents.priority import scan_and_rank, score_event
from src.services.polymarket import list_active_events, scan_active_events


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(200, {"ok": True})

    def do_GET(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/health":
                self._send_json(200, {"ok": True, "service": "polypilot-backend"})
                return

            if parsed.path == "/api/polymarket/events":
                params = parse_qs(parsed.query)
                limit = int((params.get("limit") or ["10"])[0])
                events = list_active_events(limit=limit)
                self._send_json(200, {"items": events, "count": len(events)})
                return

            if parsed.path == "/api/priority/scan":
                params = parse_qs(parsed.query)
                scan_limit = int((params.get("scan") or ["300"])[0])
                top_n = int((params.get("top") or ["10"])[0])
                pool = scan_active_events(max_events=scan_limit)
                ranking = scan_and_rank(pool, top_n=top_n, use_llm_top_k=0)
                self._send_json(200, ranking)
                return

            if parsed.path == "/api/priority/score":
                params = parse_qs(parsed.query)
                event_id = (params.get("id") or [""])[0]
                pool = scan_active_events(max_events=500)
                match = next((event for event in pool if str(event.get("id")) == str(event_id)), None)
                if not match:
                    self._send_json(404, {"error": "Event not found in active scan pool"})
                    return
                self._send_json(200, score_event(match, use_llm=False))
                return

            self._send_json(404, {"error": "Not found"})
        except Exception as error:
            self._send_json(500, {"error": str(error)})

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length") or "0")
            raw_body = self.rfile.read(length).decode("utf-8") if length else "{}"
            body = json.loads(raw_body or "{}")

            if parsed.path == "/api/agents/analyze":
                event = body.get("event")
                if not event:
                    self._send_json(400, {"error": "Expected JSON body: { \"event\": {...} }"})
                    return
                analysis = analyze_event(event)
                self._send_json(200, analysis)
                return

            self._send_json(404, {"error": "Not found"})
        except Exception as error:
            self._send_json(500, {"error": str(error)})

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    load_env()
    port = int(os.getenv("PORT", "8787"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"PolyPilot backend running on http://127.0.0.1:{port}")
    server.serve_forever()
