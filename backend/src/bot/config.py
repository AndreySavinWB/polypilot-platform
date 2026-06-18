import os


def bot_token():
    return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()


def webhook_secret():
    return os.getenv("TELEGRAM_WEBHOOK_SECRET", "").strip()


def site_base():
    return os.getenv("PP_SITE_BASE", "https://polypilot-platform.vercel.app/app").rstrip("/")


def channel_url():
    return os.getenv("TELEGRAM_CHANNEL_URL", "https://t.me/polypilot_pro").strip()


def public_backend_url():
    return os.getenv("PUBLIC_BACKEND_URL", "").rstrip("/")


def is_configured():
    return bool(bot_token())
