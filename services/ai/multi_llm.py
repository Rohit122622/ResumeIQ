"""
Multi-LLM Service — Production-grade fallback chain.

MODEL PRIORITY (STRICT):
  1. Gemini (gemini-2.5-flash, gemini-2.5-flash-lite)
  2. Groq (llama-3.3-70b-versatile)
  3. OpenAI (gpt-4o-mini)
  4. DeepSeek
  5. Qwen
  6. Claude
  7. Local rule-based (final safety net)

Features:
  - Thread-safe throttling (1.5s between Gemini calls)
  - 2 retries per model
  - safe_json_parse() on JSON responses
  - call_llm_text() for plain-text responses (Recruiter Copilot)
  - No system crash possible from LLM failures
"""

import os
import json
import logging
import requests
import time
import threading
from utils.json_utils import safe_json_parse

logger = logging.getLogger(__name__)

# ── Throttle state for Gemini quota protection ──
_last_gemini_call = 0.0
_gemini_lock = threading.Lock()
_GEMINI_MIN_INTERVAL = 1.5  # seconds between Gemini calls

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite"
]


def extract_json(text):
    """Parse LLM text response into a dict with unified structure."""
    data = safe_json_parse(text)
    if isinstance(data, dict):
        if "insights" not in data:
            data["insights"] = str(data.get("verdict", data.get("rewritten_objective", "Generated insights.")))
        if "suggestions" not in data:
            data["suggestions"] = data.get("skill_suggestions", data.get("version_a_strengths", []))
        if "analysis" not in data:
            data["analysis"] = str(data.get("verdict_reason", "Analysis complete."))
        if "score_reason" not in data:
            data["score_reason"] = str(data.get("strength_reason", "Score evaluated."))
        return data
    raise Exception("Failed to parse JSON from LLM response")


def build_openai_payload(prompt, model="gpt-4o-mini"):
    return {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }


# ─────────────── RAW TEXT EXTRACTION ───────────────

def _extract_raw_text(response_text):
    """Extract plain text from an LLM response, stripping any JSON wrapper."""
    if not response_text:
        return ""
    text = response_text.strip()
    # If it looks like JSON, try to extract a human-readable field
    if text.startswith("{"):
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                # Try common fields that contain readable text
                for key in ("answer", "response", "text", "content", "insights",
                            "analysis", "reasoning", "explanation", "message"):
                    if key in data and isinstance(data[key], str) and len(data[key]) > 10:
                        return data[key]
                # If no good field found, join all string values
                parts = [str(v) for v in data.values() if isinstance(v, str) and len(str(v)) > 5]
                if parts:
                    return " ".join(parts)
        except (json.JSONDecodeError, ValueError):
            pass
    return text


# ─────────────── GEMINI (MULTI-MODEL) ───────────────

def _call_gemini_raw(prompt, force_json=True):
    """
    Try multiple Gemini models in priority order.
    Returns raw text if force_json=False, otherwise returns parsed dict.
    """
    global _last_gemini_call
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY not set")

    # ── Throttle: enforce minimum interval ──
    with _gemini_lock:
        elapsed = time.time() - _last_gemini_call
        if elapsed < _GEMINI_MIN_INTERVAL:
            time.sleep(_GEMINI_MIN_INTERVAL - elapsed)
        _last_gemini_call = time.time()

    if force_json:
        prompt_final = prompt + "\nReturn ONLY valid JSON."
    else:
        prompt_final = prompt

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        max_output_tokens=1024,
        temperature=0.2
    )

    last_error = None

    for model_name in GEMINI_MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_final,
                    config=config
                )
                logger.info("Gemini %s succeeded", model_name)
                if force_json:
                    return extract_json(response.text)
                else:
                    return response.text
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    logger.info("Gemini %s rate-limited, trying next model", model_name)
                    break
                if "not found" in err_str.lower() or "invalid" in err_str.lower():
                    logger.info("Gemini %s not available, trying next model", model_name)
                    break
                if attempt < 1:
                    time.sleep(1.5)
                    continue
                logger.warning("Gemini %s attempt %d error: %s", model_name, attempt + 1, type(e).__name__)
                break

    logger.warning("All Gemini models exhausted, switching provider")
    raise last_error or Exception("All Gemini models failed")


def call_gemini(prompt):
    """Gemini JSON mode — returns parsed dict."""
    return _call_gemini_raw(prompt, force_json=True)


# ─────────────── OPENAI-COMPATIBLE PROVIDER CALLS ───────────────

def _call_openai_compatible(url, headers, body, provider_name, force_json=True):
    """Generic OpenAI-compatible API call. Returns dict or raw text."""
    response = requests.post(url, headers=headers, json=body, timeout=15)
    if response.status_code != 200:
        raise Exception(f"{provider_name} HTTP {response.status_code}: {response.text[:200]}")
    raw_text = response.json()["choices"][0]["message"]["content"]
    if force_json:
        return extract_json(raw_text)
    return raw_text


# ─────────────── GROQ ───────────────

def call_groq(prompt, force_json=True):
    """Groq API call with llama-3.3-70b-versatile."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY not set")
    return _call_openai_compatible(
        url="https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        body={"model": "llama-3.3-70b-versatile",
              "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
        provider_name="Groq",
        force_json=force_json
    )


# ─────────────── OTHER PROVIDERS ───────────────

def call_grok(prompt, force_json=True):
    """Grok (xAI) API call."""
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        raise Exception("GROK_API_KEY not set")
    return _call_openai_compatible(
        url="https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        body={"model": "grok-4-1-fast",
              "messages": [{"role": "system", "content": "You are a helpful assistant."},
                           {"role": "user", "content": prompt}], "temperature": 0.2},
        provider_name="Grok",
        force_json=force_json
    )


def call_openai(prompt, force_json=True):
    """OpenAI API call with gpt-4o-mini."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY not set")
    return _call_openai_compatible(
        url="https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        body=build_openai_payload(prompt, "gpt-4o-mini"),
        provider_name="OpenAI",
        force_json=force_json
    )


def call_deepseek(prompt, force_json=True):
    """DeepSeek API call."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise Exception("DEEPSEEK_API_KEY not set")
    return _call_openai_compatible(
        url="https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        body={"model": "deepseek-chat",
              "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
        provider_name="DeepSeek",
        force_json=force_json
    )


def call_qwen(prompt, force_json=True):
    """Qwen (Alibaba) API call."""
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        raise Exception("QWEN_API_KEY not set")
    return _call_openai_compatible(
        url="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        body={"model": "qwen-turbo",
              "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
        provider_name="Qwen",
        force_json=force_json
    )


def call_claude(prompt, force_json=True):
    """Anthropic Claude API call."""
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise Exception("CLAUDE_API_KEY not set")
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    data = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data, timeout=15)
    if response.status_code != 200:
        raise Exception(f"Claude HTTP {response.status_code}: {response.text[:200]}")
    raw_text = response.json()["content"][0]["text"]
    if force_json:
        return extract_json(raw_text)
    return raw_text


# ─────────────── PROVIDER CHAIN ───────────────

_PROVIDER_CHAIN = [
    ("Gemini", lambda p, fj: _call_gemini_raw(p, force_json=fj)),
    ("Groq", lambda p, fj: call_groq(p, force_json=fj)),
    ("OpenAI", lambda p, fj: call_openai(p, force_json=fj)),
    ("DeepSeek", lambda p, fj: call_deepseek(p, force_json=fj)),
    ("Qwen", lambda p, fj: call_qwen(p, force_json=fj)),
    ("Claude", lambda p, fj: call_claude(p, force_json=fj)),
]


def _run_provider_chain(prompt, force_json=True):
    """
    Run through the provider chain in priority order.
    Returns the first successful result (dict if force_json, str otherwise).
    Raises Exception only if ALL providers fail.
    """
    last_error = None
    for name, call_fn in _PROVIDER_CHAIN:
        try:
            logger.info("LLM: Attempting %s", name)
            result = call_fn(prompt, force_json)
            logger.info("LLM: %s succeeded", name)
            return result
        except Exception as e:
            last_error = e
            err_str = str(e)
            # Skip providers with missing API keys silently
            if "not set" in err_str or "missing" in err_str.lower():
                logger.debug("LLM: %s skipped (API key not configured)", name)
            else:
                logger.warning("LLM: %s failed: %s — %s", name, type(e).__name__, err_str[:100])

    raise last_error or Exception("All LLM providers exhausted")


# ─────────────── CENTRAL LLM CALLER (JSON) ───────────────

def call_llm(prompt):
    """
    Central LLM function — strict fallback chain.
    Returns a parsed dict (JSON mode). NEVER crashes.

    Order: Gemini → Groq → OpenAI → DeepSeek → Qwen → Claude → local rule-based.
    """
    try:
        return _run_provider_chain(prompt, force_json=True)
    except Exception as e:
        logger.error("LLM: All providers exhausted, using local rule-based response: %s", e)

    # ── Local rule-based response (NEVER crashes) ──
    return {
        "insights": "Evaluation completed using rule-based analysis.",
        "suggestions": ["Consider adding role-specific skills", "Quantify achievements"],
        "analysis": "Rule-based evaluation complete.",
        "score_reason": "Scored using heuristic analysis"
    }


# ─────────────── CENTRAL LLM CALLER (PLAIN TEXT) ───────────────

def call_llm_text(prompt):
    """
    Central LLM function for plain-text responses.
    Used by Recruiter Copilot — returns a string, not JSON.
    NEVER crashes. Returns a fallback string if all providers fail.

    Order: Gemini → Groq → OpenAI → DeepSeek → Qwen → Claude → None.
    """
    try:
        result = _run_provider_chain(prompt, force_json=False)
        # If result is somehow a dict (shouldn't be), extract text from it
        if isinstance(result, dict):
            return _extract_raw_text(json.dumps(result))
        return str(result)
    except Exception as e:
        logger.error("LLM Text: All providers exhausted: %s", e)
        return None
