"""Girdi doğrulama, prompt injection etiketlemesi ve hız sınırı (07-guvenlik.md)."""

import re
import time

from config import MAX_INPUT_CHARS, RATE_LIMIT_PER_MIN

# \x00-\x1F arası kontrol karakterleri (satır sonu \n, \r ve sekme \t hariç) + DEL (SEC-08)
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
# <kullanici_sorusu>, </kullanici_sorusu>, < /KULLANICI_SORUSU > gibi varyasyonlar (SEC-02)
_TAG_RE = re.compile(r"<\s*/?\s*kullanici_sorusu\s*>", re.IGNORECASE)

TAG_OPEN = "<kullanici_sorusu>"
TAG_CLOSE = "</kullanici_sorusu>"

RATE_WINDOW_S = 60


def validate_input(text: str | None) -> tuple[bool, str]:
    """Girdiyi temizler ve doğrular (SEC-06, SEC-07, SEC-08).

    Dönüş: (geçerli_mi, temiz_metin_veya_hata_mesajı).
    Boş girdi için hata mesajı "" olur (arayüz hiçbir şey göstermez).
    """
    if text is None:
        return False, ""
    cleaned = _CONTROL_CHARS.sub("", text).strip()
    if not cleaned:
        return False, ""
    if len(cleaned) > MAX_INPUT_CHARS:
        return False, f"Mesajın en fazla {MAX_INPUT_CHARS} karakter olabilir."
    return True, cleaned


def strip_tags(text: str) -> str:
    """Girdideki <kullanici_sorusu> etiketlerini siler."""
    return _TAG_RE.sub("", text)


def wrap_user_message(text: str) -> str:
    """Etiketleri temizler ve metni <kullanici_sorusu> etiketleriyle sarar (SEC-02)."""
    return f"{TAG_OPEN}\n{strip_tags(text).strip()}\n{TAG_CLOSE}"


def check_rate_limit(request_times: list[float], now: float | None = None) -> bool:
    """Son 60 saniyedeki istek sayısı sınırın altındaysa True (SEC-10).

    Listeyi yerinde günceller: 60 saniyeden eski kayıtları siler.
    İsteğin kendisini eklemek çağıranın sorumluluğundadır.
    """
    now = time.time() if now is None else now
    request_times[:] = [t for t in request_times if now - t < RATE_WINDOW_S]
    return len(request_times) < RATE_LIMIT_PER_MIN


def build_api_messages(history: list[dict], max_history: int) -> list[dict]:
    """Sohbet geçmişini modele gönderilecek biçime çevirir.

    - Yalnızca user/assistant rolleri alınır (SEC-04).
    - Son max_history mesaj gönderilir (SEC-12); liste bir user mesajıyla başlar.
    - Tüm user mesajları etiketlerle sarılır (SEC-02).
    """
    msgs = [m for m in history if m.get("role") in ("user", "assistant") and m.get("content")]
    msgs = msgs[-max_history:]
    while msgs and msgs[0]["role"] != "user":
        msgs = msgs[1:]
    return [
        {
            "role": m["role"],
            "content": wrap_user_message(m["content"]) if m["role"] == "user" else m["content"],
        }
        for m in msgs
    ]
