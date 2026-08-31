#!/usr/bin/env python3
"""
OpenRouter Model Helper — free + cheap coding models, then DeepSeek API.
Fallback chain: free → cheap coding → our DeepSeek API.
Uses OPENROUTER_API_KEY_OPENCLAW from .env.
"""
import json, subprocess
from pathlib import Path
from typing import Optional

# Phase 1: truly free models
FREE_MODELS = [
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "openrouter/free",
]

# Phase 2: cheap coding-capable models (< $0.0003/tok — MiniMax, Qwen, DeepSeek)
CHEAP_CODING = [
    "qwen/qwen3-coder-30b-a3b-instruct",   # $0.0001 — coding specialist
    "qwen/qwen3-coder-next",                 # $0.0001
    "qwen/qwen3-coder-flash",                # $0.0002 — 1M ctx
    "minimax/minimax-m2.5",                  # $0.0001 — 204k ctx
    "qwen/qwen3.6-flash",                    # $0.0002 — 1M ctx
    "qwen/qwen3.5-flash-02-23",              # $0.0001 — 1M ctx
    "deepseek/deepseek-v4-flash",            # $0.0001 — 1M ctx
]

DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"


def get_key(var_name: str) -> Optional[str]:
    """Read a named key from .env files."""
    for env_path in [
        Path("/mnt/c/Users/habib/.hermes/.env"),
        Path.home() / ".hermes" / ".env"
    ]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if var_name in line and "=" in line:
                    val = line.split("=", 1)[1].strip()
                    if val:
                        return val
    return None


def chat(prompt: str, system: str = "", model: str = "google/gemma-4-31b-it:free",
         max_tokens: int = 4096, temperature: float = 0.3,
         api_base: str = "https://openrouter.ai/api/v1/chat/completions",
         key_var: str = "OPENROUTER_API_KEY_OPENCLAW") -> str:
    """Call an LLM API. Returns response text."""
    key = get_key(key_var)
    if not key:
        return f"❌ {key_var} not found in .env"

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        r = subprocess.run(
            ["curl", "-s", api_base,
             "-H", f"Authorization: Bearer {key}",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "model": model,
                 "messages": messages,
                 "max_tokens": max_tokens,
                 "temperature": temperature,
             })],
            capture_output=True, text=True, timeout=120
        )
        data = json.loads(r.stdout)
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        elif "error" in data:
            return f"❌ Error: {data['error'].get('message', str(data['error']))}"
        return f"❌ Unexpected: {json.dumps(data)[:300]}"
    except subprocess.TimeoutExpired:
        return "❌ Request timed out (120s)"
    except Exception as e:
        return f"❌ Request failed: {e}"


def chat_with_fallback(prompt: str, system: str = "", max_tokens: int = 4096) -> str:
    """Try free → cheap coding → our DeepSeek API."""
    for model in FREE_MODELS:
        result = chat(prompt, system, model, max_tokens)
        if not result.startswith("❌"):
            return result

    for model in CHEAP_CODING:
        result = chat(prompt, system, model, max_tokens)
        if not result.startswith("❌"):
            return result

    deepseek_key = get_key("DEEPSEEK_API_KEY")
    if deepseek_key:
        for known in ["deepseek-v4-pro", "deepseek-chat", "deepseek-coder"]:
            result = chat(prompt, system, known, max_tokens,
                          api_base=DEEPSEEK_API, key_var="DEEPSEEK_API_KEY")
            if not result.startswith("❌"):
                return result

    return f"All models failed. Last error: {result}"
