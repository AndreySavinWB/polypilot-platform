"""Quick LLM connectivity test (1 event)."""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.agents.pipeline import analyze_event
from src.services.llm import has_llm_key
from src.services.polymarket import list_active_events


def load_env():
    env_path = os.path.join(ROOT, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def main():
    load_env()
    print("LLM key configured:", has_llm_key())
    print("Provider:", os.getenv("LLM_PROVIDER"))
    print("Model:", os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL"))
    event = list_active_events(limit=1)[0]
    print("Event:", event.get("title"))
    result = analyze_event(event)
    print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])


if __name__ == "__main__":
    main()
