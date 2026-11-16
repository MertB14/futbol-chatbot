"""Uygulama ayarları: modlar, temperature, güvenlik limitleri ve ortam değişkenleri."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = ROOT_DIR / "prompts"
TESTS_DIR = ROOT_DIR / "tests"

load_dotenv(ROOT_DIR / ".env")

# --- Konu modları (FR-03) ---
MODES = {
    "kurallar_taktik": "⚖️ Kurallar & Taktik",
    "turk_futbolu": "🇹🇷 Türk Futbolu",
    "dunya_futbolu": "🌍 Dünya Futbolu",
}
DEFAULT_MODE = "kurallar_taktik"

MODE_DESCRIPTIONS = {
    "kurallar_taktik": "Oyun kuralları, VAR, dizilişler ve taktikler",
    "turk_futbolu": "Süper Lig, Türk kulüpleri ve milli takım",
    "dunya_futbolu": "Avrupa ligleri, Dünya Kupası ve efsaneler",
}

WELCOME_MESSAGES = {
    "kurallar_taktik": "Merhaba! Futbol kuralları ve taktikleri hakkında soru sorabilirsin.",
    "turk_futbolu": "Merhaba! Türk futbolu, Süper Lig ve milli takım hakkında soru sorabilirsin.",
    "dunya_futbolu": "Merhaba! Dünya futbolu, büyük turnuvalar ve efsane oyuncular hakkında soru sorabilirsin.",
}

# Örnek soru butonları (06-mimari.md, Bölüm 4.4)
EXAMPLE_QUESTIONS = {
    "kurallar_taktik": [
        "Ofsayt nedir?",
        "VAR ne zaman devreye girer?",
        "4-3-3 dizilişinin güçlü ve zayıf yanları nelerdir?",
    ],
    "turk_futbolu": [
        "Türkiye'nin 2002 Dünya Kupası macerasını anlatır mısın?",
        "Galatasaray UEFA Kupası'nı nasıl kazandı?",
        "Süper Lig'de en çok şampiyon olan kulüp hangisi?",
    ],
    "dunya_futbolu": [
        "En çok Dünya Kupası kazanan ülke hangisi?",
        "Total futbol nedir?",
        "Arsenal'in yenilmezler sezonunu anlatır mısın?",
    ],
}

PROMPT_VERSION = "v1"  # Uygulamanın kullandığı prompt sürümü (05, Bölüm 6)
MAX_HISTORY = 10  # Modele gönderilen son mesaj sayısı (NFR-06, SEC-12)

# --- Temperature (FR-12) ---
TEMPERATURE_DEFAULT = 0.3
TEMPERATURE_MIN = 0.0
TEMPERATURE_MAX = 1.0
TEMPERATURE_STEP = 0.1

# --- Güvenlik (07-guvenlik.md) ---
MAX_INPUT_CHARS = 1000  # SEC-06
RATE_LIMIT_PER_MIN = 10  # SEC-10
MAX_TOKENS = 800  # SEC-11
REQUEST_TIMEOUT_S = 30  # SEC-13

# --- Uyarı metinleri (08-etik.md) ---
DISCLAIMER = (
    "Cevaplar yapay zekâ tarafından üretilir ve hatalı olabilir. "
    "Önemli bilgileri resmî kaynaklardan (TFF, UEFA, FIFA) doğrula."
)  # ETK-08
PRIVACY_NOTICE = (
    "Mesajların yanıt üretmek için üçüncü taraf bir yapay zekâ servisine gönderilir. "
    "Kişisel bilgilerini (ad, telefon, adres vb.) paylaşma."
)  # ETK-01


def env(name: str, default: str = "") -> str:
    """Ortam değişkenini okur; boşlukları temizler."""
    return os.environ.get(name, default).strip()


def env_list(name: str) -> list[str]:
    """Virgülle ayrılmış ortam değişkenini listeye çevirir."""
    return [x.strip() for x in env(name).split(",") if x.strip()]
