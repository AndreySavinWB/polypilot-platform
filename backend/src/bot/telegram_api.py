import json
import urllib.error
import urllib.request


def _call(token, method, payload=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        raw = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram API {method} failed: {raw}") from err
    data = json.loads(raw)
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API {method} error: {data}")
    return data.get("result")


def send_message(token, chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    if parse_mode is not None:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return _call(token, "sendMessage", payload)


def send_plain(token, chat_id, text, reply_markup=None):
    """Без parse_mode — надёжнее для многострочных брифов."""
    return send_message(token, chat_id, text, reply_markup=reply_markup, parse_mode=None)


def answer_callback(token, callback_id, text=None):
    payload = {"callback_query_id": callback_id}
    if text:
        payload["text"] = text
        payload["show_alert"] = False
    return _call(token, "answerCallbackQuery", payload)


def set_webhook(token, url, secret_token=None):
    payload = {"url": url, "drop_pending_updates": True}
    if secret_token:
        payload["secret_token"] = secret_token
    return _call(token, "setWebhook", payload)


def delete_webhook(token):
    return _call(token, "deleteWebhook", {"drop_pending_updates": True})


def get_updates(token, offset=None, timeout=25):
    payload = {"timeout": timeout, "allowed_updates": ["message", "callback_query"]}
    if offset is not None:
        payload["offset"] = offset
    return _call(token, "getUpdates", payload)
