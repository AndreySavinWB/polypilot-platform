import base64
import os


def apply_bot_env_blob():
    """Fallback: один Railway var PP_BOT_ENV = base64(.env telegram block)."""
    blob = os.getenv("PP_BOT_ENV", "").strip()
    if not blob:
        return
    try:
        text = base64.b64decode(blob).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


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


apply_bot_env_blob()
