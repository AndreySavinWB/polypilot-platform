import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from src.agents.pipeline import analyze_event
from src.agents.pie import run_pie
from src.agents.event_ranking import get_rank_mode, scan_and_rank, score_event
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
                ranking = scan_and_rank(
                    pool,
                    top_n=top_n,
                    use_llm_top_k=20 if get_rank_mode() == "priority" else 0,
                )
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

            if parsed.path == "/api/live/events":
                live_path = os.path.join(ROOT, "data", "events-live.json")
                if not os.path.exists(live_path):
                    self._send_json(200, {"events": [], "generatedAt": None})
                    return
                with open(live_path, "r", encoding="utf-8") as live_file:
                    self._send_json(200, json.load(live_file))
                return

            if parsed.path == "/api/telegram/health":
                from src.bot import config as bot_config

                self._send_json(200, {
                    "ok": True,
                    "telegramConfigured": bot_config.is_configured(),
                    "ceoChatConfigured": bool(bot_config.ceo_chat_id()),
                    "publicBackendConfigured": bool(bot_config.public_backend_url()),
                    "briefSecretConfigured": bool(bot_config.ceo_brief_secret()),
                    "onRailway": bool(
                        os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID")
                    ),
                    "configuredEnvKeys": sorted(
                        k for k in os.environ
                        if k.startswith("TELEGRAM_") or k in ("CEO_BRIEF_SECRET", "PUBLIC_BACKEND_URL", "DAILY_PUBLISH_START_DATE")
                    ),
                })
                return

            if parsed.path == "/api/telegram/setup-webhook":
                from src.bot import config as bot_config, telegram_api

                params = parse_qs(parsed.query)
                key = (params.get("key") or [""])[0]
                secret = bot_config.ceo_brief_secret()
                if not secret or key != secret:
                    self._send_json(403, {"error": "Invalid or missing key"})
                    return
                if not bot_config.is_configured():
                    self._send_json(503, {"error": "TELEGRAM_BOT_TOKEN not set on server"})
                    return
                base = bot_config.public_backend_url()
                if not base:
                    self._send_json(503, {"error": "PUBLIC_BACKEND_URL not set on server"})
                    return
                token = bot_config.bot_token()
                hook = f"{base}/api/telegram/webhook"
                wh_secret = bot_config.webhook_secret() or None
                result = telegram_api.set_webhook(token, hook, secret_token=wh_secret)
                self._send_json(200, {"ok": True, "webhook": hook, "telegram": result})
                return

            if parsed.path == "/api/ceo/brief/send":
                from src.bot import config as bot_config
                from src.bot.ceo_brief import send_morning_brief_to_ceo

                params = parse_qs(parsed.query)
                key = (params.get("key") or [""])[0]
                secret = bot_config.ceo_brief_secret()
                if not secret or key != secret:
                    self._send_json(403, {"error": "Invalid or missing key"})
                    return
                if not bot_config.is_configured():
                    self._send_json(503, {"error": "TELEGRAM_BOT_TOKEN not set on server"})
                    return
                if not bot_config.ceo_chat_id():
                    self._send_json(503, {"error": "TELEGRAM_CEO_CHAT_ID not set on server"})
                    return
                result = send_morning_brief_to_ceo()
                self._send_json(200, result)
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

            if parsed.path == "/api/pie/process":
                event = body.get("event")
                if not event:
                    self._send_json(400, {"error": "Expected JSON body: { \"event\": {...} }"})
                    return
                priority = body.get("priority")
                package = run_pie(event, priority_result=priority)
                self._send_json(200, package)
                return

            if parsed.path == "/api/telegram/webhook":
                from src.bot import config as bot_config, handlers as bot_handlers

                if not bot_config.is_configured():
                    self._send_json(503, {"error": "Telegram bot is not configured"})
                    return
                secret = bot_config.webhook_secret()
                if secret:
                    header = self.headers.get("X-Telegram-Bot-Api-Secret-Token")
                    if header != secret:
                        self._send_json(403, {"error": "Invalid webhook secret"})
                        return
                result = bot_handlers.handle_update(body)
                self._send_json(200, result)
                return

            self._send_json(404, {"error": "Not found"})
        except Exception as error:
            self._send_json(500, {"error": str(error)})

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    load_env()
    port = int(os.getenv("PORT", "8787"))
    host = os.getenv("HOST", "0.0.0.0")
    from src.bot import config as bot_config

    has_tg = bot_config.is_configured()
    has_ceo = bool(bot_config.ceo_chat_id())
    print(f"[boot] telegram_token={'yes' if has_tg else 'NO'} ceo_chat={'yes' if has_ceo else 'NO'}")
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"PolyPilot backend running on http://{host}:{port}")
    server.serve_forever()
