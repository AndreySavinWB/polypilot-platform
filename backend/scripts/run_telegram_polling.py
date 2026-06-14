"""Local polling mode for Telegram bot (dev / until Railway webhook is live)."""

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from server import load_env
from src.bot import config, handlers, telegram_api


def main():
    load_env()
    token = config.bot_token()
    if not token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in backend/.env")

    print("PolyPilot bot polling… Ctrl+C to stop")
    telegram_api.delete_webhook(token)
    offset = None
    while True:
        try:
            updates = telegram_api.get_updates(token, offset=offset, timeout=25)
            for update in updates:
                offset = update["update_id"] + 1
                handlers.handle_update(update, token)
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as err:
            print("Error:", err)
            time.sleep(3)


if __name__ == "__main__":
    main()
