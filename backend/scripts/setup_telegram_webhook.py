"""Register Telegram webhook (run once after deploy)."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from server import load_env
from src.bot import config, telegram_api


def main():
    load_env()
    token = config.bot_token()
    base = config.public_backend_url()
    if not token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in backend/.env")
    if not base:
        raise SystemExit("Set PUBLIC_BACKEND_URL (e.g. https://your-app.up.railway.app)")

    secret = config.webhook_secret() or None
    url = f"{base}/api/telegram/webhook"
    result = telegram_api.set_webhook(token, url, secret_token=secret)
    print("Webhook set:", url)
    print(result)


if __name__ == "__main__":
    main()
