import os


def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1].strip()
    return value


def bot_token():
    return _env("TELEGRAM_BOT_TOKEN")


def webhook_secret():
    return _env("TELEGRAM_WEBHOOK_SECRET")


def site_base():
    return os.getenv("PP_SITE_BASE", "https://polypilot-platform.vercel.app/app").rstrip("/")


def channel_url():
    return _env("TELEGRAM_CHANNEL_URL") or "https://t.me/polypilot_pro"


def ceo_brief_secret() -> str:
    return _env("CEO_BRIEF_SECRET") or _env("TELEGRAM_WEBHOOK_SECRET")


def public_backend_url():
    return _env("PUBLIC_BACKEND_URL").rstrip("/")


def ceo_chat_id():
    return _env("TELEGRAM_CEO_CHAT_ID")


def is_configured():
    return bool(bot_token())
