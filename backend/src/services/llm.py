import json
import os
from urllib.request import Request, urlopen


PROVIDERS = {
    "openai": {
        "base_url": "https://api.openai.com/v1/chat/completions",
        "model_prefix": "",
    },
    "polza": {
        "base_url": "https://polza.ai/api/v1/chat/completions",
        "model_prefix": "openai/",
    },
}


def get_api_key():
    return (
        os.getenv("POLZA_API_KEY")
        or os.getenv("LLM_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or ""
    ).strip()


def has_llm_key():
    return bool(get_api_key())


def _resolve_model(provider_name, model):
    provider = PROVIDERS.get(provider_name, PROVIDERS["openai"])
    if provider_name == "polza" and model and "/" not in model:
        return f"{provider['model_prefix']}{model}"
    return model


def ask_llm(system_prompt, user_payload):
    """OpenAI-compatible chat completion (OpenAI or Polza.ai)."""
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("LLM API key is not configured")

    provider_name = (os.getenv("LLM_PROVIDER") or "openai").strip().lower()
    provider = PROVIDERS.get(provider_name)
    if not provider:
        raise RuntimeError(f"Unknown LLM_PROVIDER: {provider_name}")

    base_url = os.getenv("LLM_BASE_URL") or provider["base_url"]
    model = _resolve_model(
        provider_name,
        os.getenv("OPENAI_MODEL") or os.getenv("LLM_MODEL") or "gpt-4o-mini",
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    request = Request(
        base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(request, timeout=90) as response:
        data = json.loads(response.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"]
    return json.loads(content)
