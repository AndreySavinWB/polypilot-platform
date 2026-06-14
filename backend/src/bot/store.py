import json
import os
import threading
from datetime import datetime, timezone


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(ROOT, "data")
USERS_PATH = os.path.join(DATA_DIR, "bot_users.json")
APPLICATIONS_PATH = os.path.join(DATA_DIR, "bot_starter_applications.json")

_lock = threading.Lock()


def _read(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(user_id):
    with _lock:
        users = _read(USERS_PATH, {})
        return users.get(str(user_id))


def set_user(user_id, patch):
    with _lock:
        users = _read(USERS_PATH, {})
        row = users.get(str(user_id), {})
        row.update(patch)
        row["updatedAt"] = datetime.now(timezone.utc).isoformat()
        users[str(user_id)] = row
        _write(USERS_PATH, users)
        return row


def save_starter_application(user_id, username, text):
    with _lock:
        items = _read(APPLICATIONS_PATH, [])
        entry = {
            "userId": user_id,
            "username": username,
            "text": text,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        items.append(entry)
        _write(APPLICATIONS_PATH, items)
        return entry
