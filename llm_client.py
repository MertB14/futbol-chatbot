"""LLM API istemcisi. Sağlayıcıya özel tek modül (NFR-04).

OpenCode Go OpenAI uyumlu bir API sunduğu için `openai` SDK'sı `base_url` ile kullanılır.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Callable

import openai
from openai import OpenAI

from config import (
    MAX_TOKENS,
    REQUEST_TIMEOUT_S,
    TEMPERATURE_DEFAULT,
    TEMPERATURE_MAX,
    TEMPERATURE_MIN,
    env,
)

logger = logging.getLogger("futbol_asistani.llm")


# Hata türleri -> arayüzde gösterilecek genel Türkçe mesaj (06-mimari.md, Bölüm 4.3)
ERROR_MESSAGES = {
    "auth": "Asistana şu anda ulaşılamıyor. Lütfen yöneticiye bildir.",
    "timeout": "Cevap zamanında gelmedi. Lütfen tekrar dene.",
    "quota": "Kullanım sınırına ulaşıldı. Lütfen daha sonra tekrar dene.",
    "other": "Bir hata oluştu. Lütfen tekrar dene.",
}


class LLMError(Exception):
    """API anahtarı içermeyen, kullanıcıya gösterilebilir hata (SEC-16)."""

    def __init__(self, kind: str, detail: str = ""):
        self.kind = kind if kind in ERROR_MESSAGES else "other"
        self.detail = detail  # Yalnızca konsol/test çıktısı için; anahtar maskelenmiş
        super().__init__(ERROR_MESSAGES[self.kind])

    @property
    def user_message(self) -> str:
        return ERROR_MESSAGES[self.kind]


@dataclass
class ChatResult:
    text: str
    model: str  # Cevabı üreten model (ana ya da yedek)
    used_fallback: bool  # FR-16
    latency_s: float  # İstekten son parçaya kadar geçen süre (FR-15)
    first_token_s: float | None  # İlk içerik parçasının gelme süresi
    prompt_tokens: int | None
    completion_tokens: int | None
    tokens_estimated: bool  # Sağlayıcı usage döndürmezse True


class _PartialStreamError(Exception):
    """Cevabın bir kısmı geldikten sonra oluşan hata: yedek modele geçilmez."""

    def __init__(self, original: Exception):
        self.original = original


_client: OpenAI | None = None
_client_key: tuple[str, str] | None = None


def _mask(text: str) -> str:
    """Metindeki API anahtarını maskeler."""
    key = env("OPENCODE_API_KEY")
    if key and len(key) >= 6:
        text = text.replace(key, key[:3] + "***")
    return text


def _get_client() -> OpenAI:
    global _client, _client_key
    api_key = env("OPENCODE_API_KEY")
    base_url = env("LLM_BASE_URL")
    if not api_key or api_key == "buraya-anahtarinizi-yazin":
        raise LLMError("auth", "OPENCODE_API_KEY tanımlı değil")
    if not base_url:
        raise LLMError("auth", "LLM_BASE_URL tanımlı değil")
    if _client is None or _client_key != (api_key, base_url):
        _client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=REQUEST_TIMEOUT_S,
            max_retries=1,  # SEC-13
        )
        _client_key = (api_key, base_url)
    return _client


def default_model() -> str:
    return env("LLM_MODEL", "deepseek-v4.1-flash-free")


def fallback_model() -> str:
    return env("LLM_FALLBACK_MODEL")


def clamp_temperature(t: float) -> float:
    """SEC-09: temperature değerini [0.0, 1.0] aralığına sıkıştırır."""
    try:
        t = float(t)
    except (TypeError, ValueError):
        return TEMPERATURE_DEFAULT
    return max(TEMPERATURE_MIN, min(TEMPERATURE_MAX, t))


def _estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


def _classify(exc: Exception) -> str:
    if isinstance(exc, LLMError):
        return exc.kind
    if isinstance(exc, (openai.APITimeoutError, openai.APIConnectionError)):
        return "timeout"
    if isinstance(exc, (openai.AuthenticationError, openai.PermissionDeniedError, openai.NotFoundError)):
        return "auth"  # Geçersiz anahtar veya yanlış model adı: yapılandırma sorunu
    if isinstance(exc, openai.RateLimitError):
        return "quota"
    return "other"


def _is_retryable(exc: Exception) -> bool:
    """Yedek modele geçilecek hatalar: zaman aşımı, 5xx, 429, 404 (FR-16)."""
    if isinstance(exc, (openai.APITimeoutError, openai.APIConnectionError)):
        return True
    if isinstance(exc, openai.APIStatusError):
        return exc.status_code in (404, 429) or exc.status_code >= 500
    return False


def _stream_once(
    client: OpenAI,
    model: str,
    messages: list[dict],
    temperature: float,
    on_token: Callable[[str], None] | None,
    include_usage: bool,
) -> ChatResult:
    start = time.perf_counter()
    kwargs = dict(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=MAX_TOKENS,  # SEC-11
        stream=True,
    )
    if include_usage:
        kwargs["stream_options"] = {"include_usage": True}

    stream = client.chat.completions.create(**kwargs)

    parts: list[str] = []
    first_token_s: float | None = None
    usage = None
    try:
        for chunk in stream:
            if getattr(chunk, "usage", None):
                usage = chunk.usage
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            piece = getattr(delta, "content", None) or ""
            if not piece:
                continue
            if first_token_s is None:
                first_token_s = time.perf_counter() - start
            parts.append(piece)
            if on_token:
                on_token(piece)
    except Exception as exc:  # noqa: BLE001
        if parts:
            raise _PartialStreamError(exc) from exc
        raise

    latency = time.perf_counter() - start
    text = "".join(parts)

    if usage and getattr(usage, "completion_tokens", None) is not None:
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        estimated = False
    else:
        prompt_chars = sum(len(m["content"]) for m in messages)
        prompt_tokens = max(1, round(prompt_chars / 4))
        completion_tokens = _estimate_tokens(text) if text else 0
        estimated = True

    return ChatResult(
        text=text,
        model=model,
        used_fallback=False,
        latency_s=round(latency, 2),
        first_token_s=round(first_token_s, 2) if first_token_s is not None else None,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        tokens_estimated=estimated,
    )


def _call_model(
    client: OpenAI,
    model: str,
    messages: list[dict],
    temperature: float,
    on_token: Callable[[str], None] | None,
) -> ChatResult:
    try:
        return _stream_once(client, model, messages, temperature, on_token, include_usage=True)
    except openai.BadRequestError as exc:
        # Bazı sağlayıcılar stream_options desteklemez; bir kez onsuz dene.
        if "stream_options" in str(exc) or "include_usage" in str(exc):
            return _stream_once(client, model, messages, temperature, on_token, include_usage=False)
        raise


def chat(
    system_prompt: str,
    messages: list[dict],
    temperature: float = TEMPERATURE_DEFAULT,
    model: str | None = None,
    use_fallback: bool = True,
    on_token: Callable[[str], None] | None = None,
) -> ChatResult:
    """Modeli çağırır ve cevabı döner.

    messages: [{"role": "user"|"assistant", "content": str}, ...]
    Sistem promptu yalnızca `system` rolünde gönderilir (SEC-03).
    Hata durumunda API anahtarını içermeyen bir LLMError fırlatır (SEC-16).
    """
    client = _get_client()
    primary = model or default_model()
    temperature = clamp_temperature(temperature)
    api_messages = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]}
        for m in messages
        if m.get("role") in ("user", "assistant")  # SEC-04
    ]

    try:
        return _call_model(client, primary, api_messages, temperature, on_token)
    except _PartialStreamError as exc:
        logger.error("Akış yarıda kesildi (%s): %s", primary, _mask(repr(exc.original)))
        raise LLMError(_classify(exc.original), _mask(str(exc.original))) from None
    except Exception as exc:  # noqa: BLE001
        logger.warning("Ana model hatası (%s): %s", primary, _mask(repr(exc)))
        backup = fallback_model()
        if not (use_fallback and backup and backup != primary and _is_retryable(exc)):
            raise LLMError(_classify(exc), _mask(str(exc))) from None

    # Yedek model (FR-16)
    try:
        result = _call_model(client, backup, api_messages, temperature, on_token)
        result.used_fallback = True
        return result
    except _PartialStreamError as exc:
        logger.error("Yedek modelde akış kesildi (%s): %s", backup, _mask(repr(exc.original)))
        raise LLMError(_classify(exc.original), _mask(str(exc.original))) from None
    except Exception as exc:  # noqa: BLE001
        logger.error("Yedek model hatası (%s): %s", backup, _mask(repr(exc)))
        raise LLMError(_classify(exc), _mask(str(exc))) from None
