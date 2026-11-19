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


# --- Kişisel veri tespiti (ETK-11) ---------------------------------------------------
# Mesaj modele gitmeden önce telefon, T.C. kimlik no, e-posta, IBAN, kart no ve adres
# aranır; bulunanlar etiketle değiştirilir ve kullanıcı uyarılır. Futbol metinlerindeki
# skor (3-1), yıl (1998-2002) ve forma numaraları yanlış alarm vermesin diye kalıplar
# en az 10 rakam ister; kimlik ve kart numaraları ayrıca sağlama algoritmasıyla doğrulanır.

_LETTER = "A-Za-zÇĞİÖŞÜçğıöşü"
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
_IBAN_RE = re.compile(r"\bTR\s?\d{2}(?:\s?\d{4}){5}\s?\d{2}\b", re.IGNORECASE)
_CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")
_TCKN_RE = re.compile(r"(?<!\d)[1-9]\d{10}(?!\d)")
_PHONE_RE = re.compile(
    r"(?<![\d+])(?:(?:\+|00)\s?90[\s.-]?|0[\s.-]?)?\(?[2-5]\d{2}\)?[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}(?!\d)"
)
_ADDRESS_WORD_RE = re.compile(
    rf"(?:[{_LETTER}0-9.]+\s+){{0,2}}"
    r"(?:mahallesi|mahalle|mah\.|sokağı|sokak|sok\.|sk\.|caddesi|cadde|cad\.|bulvarı|"
    r"apartmanı|apt\.?|sitesi|blok)"
    rf"(?![{_LETTER}])",
    re.IGNORECASE,
)
_ADDRESS_NO_RE = re.compile(
    r"(?<![\w])(?:kapı\s*no|no|daire|d)\s*[:.]?\s*\d+(?:\s*/\s*\d+)?",
    re.IGNORECASE,
)

PII_LABELS = {
    "email": "e-posta adresi",
    "iban": "IBAN",
    "kart": "kart numarası",
    "tckn": "T.C. kimlik numarası",
    "telefon": "telefon numarası",
    "adres": "adres",
}


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def _valid_tckn(n: str) -> bool:
    d = [int(c) for c in n]
    if len(d) != 11 or d[0] == 0:
        return False
    if ((sum(d[0:9:2]) * 7 - sum(d[1:8:2])) % 10) != d[9]:
        return False
    return sum(d[:10]) % 10 == d[10]


def _valid_luhn(n: str) -> bool:
    total = 0
    for i, c in enumerate(reversed(n)):
        x = int(c)
        if i % 2:
            x = x * 2 - 9 if x > 4 else x * 2
        total += x
    return total % 10 == 0


def mask_personal_data(text: str) -> tuple[str, list[str]]:
    """Mesajdaki kişisel bilgileri [TELEFON] gibi etiketlerle değiştirir (ETK-11).

    Dönüş: (maskelenmiş_metin, bulunan_türler). Türler PII_LABELS anahtarlarıdır.
    Ad-soyad tespit edilmez: oyuncu adlarıyla ayırt edilemez.
    """
    found: list[str] = []

    def sub(pattern: re.Pattern, kind: str, check=None) -> None:
        nonlocal text

        def repl(m: re.Match) -> str:
            if check and not check(m.group(0)):
                return m.group(0)
            if kind not in found:
                found.append(kind)
            return f"[{kind.upper()}]"

        text = pattern.sub(repl, text)

    sub(_EMAIL_RE, "email")
    sub(_IBAN_RE, "iban")
    sub(_CARD_RE, "kart", lambda s: 13 <= len(_digits(s)) <= 19 and _valid_luhn(_digits(s)))
    sub(_TCKN_RE, "tckn", _valid_tckn)
    sub(_PHONE_RE, "telefon")
    # Adres: "Mahallesi/Sokak..." kelimesi ile "No: 5 / Daire 3" birlikte geçerse
    if _ADDRESS_WORD_RE.search(text) and _ADDRESS_NO_RE.search(text):
        text = _ADDRESS_WORD_RE.sub("[ADRES]", text)
        text = _ADDRESS_NO_RE.sub("[ADRES]", text)
        text = re.sub(r"\[ADRES\](?:[\s,./-]*\[ADRES\])+", "[ADRES]", text)
        found.append("adres")
    return text, found


def personal_data_warning(kinds: list[str]) -> str:
    names = [PII_LABELS[k] for k in kinds]
    joined = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " ve " + names[-1]
    return (
        f"Mesajında kişisel bilgi fark ettim ({joined}). Gizliliğin için bu kısmı gizleyerek "
        "gönderdim; futbol sorularına cevap vermem için bu bilgilere gerek yok. Lütfen telefon, kimlik numarası, adres gibi bilgilerini paylaşma."
    )
