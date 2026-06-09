import json
import os
from urllib.request import Request, urlopen


PROVIDERS = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "default_model": "openai/gpt-4o-mini",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-4o-mini",
    },
    "polza": {
        "base_url": "https://polza.ai/api/v1/chat/completions",
        "default_model": "openai/gpt-4o-mini",
        "model_prefix": "openai/",
    },
}

PROVIDER_KEY_NAMES = {
    "openrouter": ("OPENROUTER_API_KEY",),
    "openai": ("OPENAI_API_KEY",),
    "polza": ("POLZA_API_KEY",),
}

FALLBACK_KEY_NAMES = ("LLM_API_KEY", "OPENROUTER_API_KEY", "POLZA_API_KEY", "OPENAI_API_KEY")


def get_provider_name():
    return (os.getenv("LLM_PROVIDER") or "polza").strip().lower()


def get_api_key():
    provider = get_provider_name()
    for key_name in PROVIDER_KEY_NAMES.get(provider, ()) + FALLBACK_KEY_NAMES:
        value = (os.getenv(key_name) or "").strip()
        if value:
            return value
    return ""


def has_llm_key():
    return bool(get_api_key())


def _resolve_model(provider_name, model):
    provider = PROVIDERS.get(provider_name, PROVIDERS["polza"])
    model = (model or provider.get("default_model") or "openai/gpt-4o-mini").strip()

    if provider_name == "polza" and model and "/" not in model:
        prefix = provider.get("model_prefix", "")
        return f"{prefix}{model}"

    if provider_name == "openrouter" and model and "/" not in model:
        return f"openai/{model}"

    return model


def _build_headers(provider_name, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if provider_name == "openrouter":
        headers["HTTP-Referer"] = (
            os.getenv("OPENROUTER_HTTP_REFERER") or "https://polypilot-platform.vercel.app"
        )
        headers["X-Title"] = os.getenv("OPENROUTER_APP_NAME") or "PolyPilot"
    return headers


def ask_llm(system_prompt, user_payload):
    """OpenAI-compatible chat completion (OpenRouter, OpenAI, Polza)."""
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("LLM API key is not configured")

    provider_name = get_provider_name()
    provider = PROVIDERS.get(provider_name)
    if not provider:
        raise RuntimeError(f"Unknown LLM_PROVIDER: {provider_name}")

    base_url = os.getenv("LLM_BASE_URL") or provider["base_url"]
    model = _resolve_model(
        provider_name,
        os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL"),
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
        headers=_build_headers(provider_name, api_key),
        method="POST",
    )
    with urlopen(request, timeout=90) as response:
        data = json.loads(response.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"]
    return json.loads(content)
