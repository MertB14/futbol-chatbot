# 06 – Mimari

## 1. Genel Bakış

```
┌──────────────────────┐
│     Kullanıcı        │
└─────────┬────────────┘
          │ soru
┌─────────▼────────────────────────────────────┐
│  app.py (Streamlit)                          │
│  - Kenar çubuğu: mod, temperature, temizle   │
│  - st.chat_message / st.chat_input           │
│  - st.session_state: messages, mode,         │
│    temperature, request_times                │
└─────────┬────────────────────────────────────┘
          │ ham girdi
┌─────────▼──────────────┐
│ security.py            │  ← Doğrulama, temizleme,
│                        │    hız sınırı, etiketleme
└─────────┬──────────────┘
          │ messages + mod + temperature
┌─────────▼──────────────┐    ┌──────────────────────┐
│ prompt_loader.py       │◄───│ prompts/*.md         │
│ base + mod promptu     │    └──────────────────────┘
└─────────┬──────────────┘
          │ sistem promptu
┌─────────▼──────────────┐
│ llm_client.py          │  ← Sağlayıcıya özel tek modül
│ chat(system, messages, │
│      temperature)      │
└─────────┬──────────────┘
          │ HTTPS (OpenAI uyumlu)
┌─────────▼──────────────────────────┐
│ OpenCode Go                        │
│ deepseek-v4.1-flash-free           │
└────────────────────────────────────┘

run_tests.py ── tests/test_questions.json ──► llm_client.py ──► tests/results/
```

## 2. Klasör Yapısı

```
futbol-chatbot/
├── app.py                  # Streamlit arayüzü
├── llm_client.py           # LLM API soyutlaması
├── prompt_loader.py        # Sistem promptunu birleştirir
├── security.py             # Girdi doğrulama, hız sınırı, etiketleme
├── config.py               # Modlar, temperature ve güvenlik limitleri
├── run_tests.py            # Otomatik test scripti
├── prompts/
│   ├── v0/base.md          # Minimal prompt (karşılaştırma tabanı)
│   ├── v1/                 # base.md + 3 mod dosyası
│   └── v2/                 # İyileştirilmiş sürüm
├── tests/
│   ├── test_questions.json
│   └── results/            # Script çıktıları
├── docs/                   # Bu dokümanlar
├── .env.example            # API anahtarı, base URL, ana/yedek/karşılaştırma modelleri
├── .gitignore              # .env, tests/results/
├── requirements.txt
└── README.md
```

## 3. Bileşenler

### `config.py`
```python
MODES = {
    "kurallar_taktik": "⚖️ Kurallar & Taktik",
    "turk_futbolu":    "🇹🇷 Türk Futbolu",
    "dunya_futbolu":   "🌍 Dünya Futbolu",
}
DEFAULT_MODE = "kurallar_taktik"
PROMPT_VERSION = "v1"   # Uygulamanın kullandığı prompt sürümü (05, Bölüm 6)
MAX_HISTORY = 10        # Modele gönderilen son mesaj sayısı (NFR-06, SEC-12)

# Temperature (FR-12)
TEMPERATURE_DEFAULT = 0.3
TEMPERATURE_MIN = 0.0
TEMPERATURE_MAX = 1.0
TEMPERATURE_STEP = 0.1

# Güvenlik (07-guvenlik.md)
MAX_INPUT_CHARS = 1000      # SEC-06
RATE_LIMIT_PER_MIN = 10     # SEC-10
MAX_TOKENS = 800            # SEC-11
REQUEST_TIMEOUT_S = 30      # SEC-13
```

### `.env.example`
```bash
OPENCODE_API_KEY=buraya-anahtarinizi-yazin
LLM_BASE_URL=https://opencode.ai/zen/go/v1
LLM_MODEL=deepseek-v4.1-flash-free           # Ana model
LLM_FALLBACK_MODEL=<model-2>                  # Yedek model (FR-16), boş bırakılırsa kapalı
LLM_COMPARE_MODELS=deepseek-v4.1-flash-free,<model-2>,<model-3>   # run_tests.py --models varsayılanı
```
> Base URL ve model kimlikleri OpenCode Go dokümanlarından doğrulanmalıdır.

### `llm_client.py`
OpenCode Go, OpenAI uyumlu bir API sunar. Bu yüzden `openai` Python SDK'sı `base_url` parametresiyle kullanılır. Sağlayıcı değişirse yalnızca bu dosya ve `.env` değişir (NFR-04).

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENCODE_API_KEY"],
    base_url=os.environ["LLM_BASE_URL"],
    timeout=REQUEST_TIMEOUT_S,
    max_retries=1,
)

@dataclass
class ChatResult:
    text: str
    model: str               # Cevabı üreten model (ana ya da yedek)
    used_fallback: bool      # FR-16
    latency_s: float         # İstekten son parçaya kadar geçen süre (FR-15)
    first_token_s: float     # İlk parçanın gelme süresi (streaming)
    prompt_tokens: int | None
    completion_tokens: int | None
    tokens_estimated: bool   # Sağlayıcı usage döndürmezse True

def chat(system_prompt: str, messages: list[dict],
         temperature: float = TEMPERATURE_DEFAULT,
         model: str | None = None,          # None -> LLM_MODEL
         use_fallback: bool = True,
         on_token: Callable[[str], None] | None = None) -> ChatResult:
    """messages: [{"role": "user"|"assistant", "content": str}, ...]
    temperature [0.0, 1.0] aralığına sıkıştırılır (SEC-09).
    max_tokens=MAX_TOKENS ile çağrılır (SEC-11).
    on_token verilirse cevap streaming ile parça parça bu fonksiyona iletilir.
    Hata durumunda, API anahtarını içermeyen bir LLMError fırlatır (SEC-16)."""
```

**Yedek model mantığı (FR-16):**
1. İstek ana modelle gönderilir.
2. Şu hatalardan biri gelirse ve `use_fallback=True` ise istek bir kez `LLM_FALLBACK_MODEL` ile tekrarlanır: zaman aşımı, 5xx sunucu hatası, 429 (hız/kota sınırı), 404 (model bulunamadı).
3. 401 (geçersiz API anahtarı) ve 400 (hatalı istek) hatalarında yedek modele geçilmez; yedek model de aynı hatayı verir.
4. Streaming sırasında cevabın bir kısmı geldikten sonra hata olursa yedek modele geçilmez; kullanıcıya hata gösterilir (yarım cevap ile yeni cevap karışmasın).

**Token ölçümü (FR-15):** Streaming isteklerde `stream_options={"include_usage": True}` gönderilir; son parçadaki `usage` alanından token sayıları okunur. Sağlayıcı bunu desteklemiyorsa token sayısı yaklaşık olarak `len(metin) / 4` ile hesaplanır ve `tokens_estimated=True` işaretlenir.

### `security.py`
```python
def validate_input(text: str) -> tuple[bool, str]:
    """Boşluk/kontrol karakteri temizler, boş ve 1000+ karakterlik
    girdiyi reddeder. (geçerli_mi, temiz_metin_veya_hata_mesajı) döner.
    SEC-06, SEC-07, SEC-08"""

def wrap_user_message(text: str) -> str:
    """Girdideki <kullanici_sorusu> etiketlerini temizler ve metni
    bu etiketlerle sarar. SEC-02"""

def check_rate_limit(request_times: list[float]) -> bool:
    """Son 60 saniyedeki istek sayısı RATE_LIMIT_PER_MIN altındaysa True. SEC-10"""
```

### `app.py` – akış
1. `st.session_state` içinde `messages`, `mode`, `temperature` ve `request_times` yoksa başlatılır.
2. Kenar çubuğu:
   - `st.radio` ile mod seçimi. Mod değişirse `messages` sıfırlanır (FR-06).
   - `st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)` ve altında kısa açıklama: "Düşük: daha tutarlı · Yüksek: daha yaratıcı" (FR-12).
   - "Sohbeti Temizle" butonu (FR-05).
3. Geçmiş mesajlar `st.chat_message` ve `st.markdown` ile çizilir (HTML kapalı, SEC-15).
4. `st.chat_input(max_chars=MAX_INPUT_CHARS)` ile yeni soru alınır.
5. `security.validate_input` ve `security.check_rate_limit` kontrolleri yapılır. Başarısız olursa `st.warning` gösterilir ve istek gönderilmez.
6. Temiz mesaj `messages`'a eklenir. Modele gönderilirken son mesaj `wrap_user_message` ile sarılır.
7. `llm_client.chat(system, messages[-MAX_HISTORY:], temperature, on_token=...)` çağrılır; cevap parça parça ekrana yazılır.
8. Cevap, `ChatResult` bilgileriyle (model, süre, token, yedek model kullanıldı mı) birlikte `messages`'a eklenir. `LLMError` yakalanırsa `st.error` ile genel bir Türkçe mesaj gösterilir (FR-11, SEC-16).
9. Her asistan cevabının altında:
   - `st.caption("2.1 sn · 340 token")`. Token tahminiyse "~340 token" yazılır (FR-15).
   - Yedek model kullanıldıysa `st.caption("ℹ️ Ana model yanıt vermediği için yedek model kullanıldı.")` (FR-16).
   - `st.feedback("thumbs", key=f"fb_{i}")` ile 👍/👎. Seçim `messages[i]["feedback"]` alanına yazılır (FR-14).
10. Kenar çubuğunda oturum özeti: "👍 5 · 👎 1" ve son cevabın modeli.

### `run_tests.py` – akış (FR-10)
1. `tests/test_questions.json` okunur.
2. Her soru, belirtilen moda göre sistem promptuyla `REPEAT` (varsayılan 3) kez çalıştırılır.
3. `cok_turlu` sorular için önceki sorunun soru-cevap çifti bağlama eklenir (`depends_on` alanı).
4. Çıktılar `tests/results/results_<YYYYMMDD_HHMM>.json` ve `.csv` dosyalarına yazılır. Puan sütunları elle doldurulmak üzere boş bırakılır.
5. Komut satırı seçenekleri: `--mode`, `--repeat`, `--ids`, `--temperature` (varsayılan 0.3, FR-13), `--prompt-version` (varsayılan v1), `--delay` (istekler arası bekleme, varsayılan 1 sn, SEC-14).
   - `--model <ad>`: tek bir modelle çalıştırır (varsayılan `LLM_MODEL`).
   - `--models a,b,c`: her modeli sırayla çalıştırır (varsayılan `LLM_COMPARE_MODELS`, FR-17).
   - `--use-fallback`: yedek modeli açar. Varsayılan **kapalı**; böylece her sonuç gerçekten istenen modele ait olur (FR-16).
   - `--blind`: kör puanlama dosyası üretir (`blind_<tarih>.csv`): satırlar karışık sırada, model adı yerine A/B/C kodu. Eşleşme ayrı bir `blind_key_<tarih>.json` dosyasına yazılır (04, Bölüm 8.2).
6. Konsola özet yazılır (model bazında): soru sayısı, ortalama süre, ortalama token, hata sayısı.

## 4. Arayüz Tasarımı (Kullanılabilirlik)

### 4.1 Ekran taslağı

```
┌─────────────────────────┬──────────────────────────────────────────────┐
│ ⚽ Futbol Asistanı      │  ⚽ Futbol Asistanı                          │
│                         │  Mod: ⚖️ Kurallar & Taktik                   │
│ Konu modu               │                                              │
│ ◉ ⚖️ Kurallar & Taktik  │  🤖 Merhaba! Futbol kuralları ve taktikleri  │
│ ○ 🇹🇷 Türk Futbolu       │     hakkında soru sorabilirsin.              │
│ ○ 🌍 Dünya Futbolu      │                                              │
│ Oyun kuralları, VAR,    │  Örnek sorular:                              │
│ dizilişler ve taktikler │  [Ofsayt nedir?] [VAR ne zaman devreye       │
│                         │   girer?] [4-3-3'ün zayıf yanları]           │
│ Temperature      0.3    │                                              │
│ ├──●────────────┤       │  👤 Ofsayt nedir?                            │
│ Düşük: tutarlı          │  🤖 Ofsayt, bir oyuncunun...                 │
│ Yüksek: yaratıcı        │     2.1 sn · 340 token        [👍] [👎]      │
│                         │                                              │
│ Bu oturum: 👍 5 · 👎 1  │                                              │
│                         │                                              │
│ [🗑️ Sohbeti Temizle]     │                                              │
│                         │  ┌────────────────────────────────────────┐  │
│ ℹ️ Cevaplar yapay zekâ  │  │ Futbolla ilgili sorunu yaz... (0/1000) │  │
│ tarafından üretilir ve  │  └────────────────────────────────────────┘  │
│ hatalı olabilir.        │                                              │
└─────────────────────────┴──────────────────────────────────────────────┘
```

### 4.2 Kullanılabilirlik kararları

| Öğe | Davranış | Amaç |
|---|---|---|
| Karşılama mesajı | Sohbet boşken, seçili moda göre bir karşılama mesajı gösterilir. Bu mesaj modele gönderilmez. | Kullanıcı ne sorabileceğini hemen anlar (H7) |
| Örnek soru butonları | Her mod için 3 örnek soru; tıklayınca soru gönderilir. Sohbet başladıktan sonra gizlenir. | Boş ekran sorununu çözer; demoyu hızlandırır |
| Mod açıklaması | Radyo butonunun altında seçili modun tek satırlık açıklaması yer alır | Modlar arasındaki fark anlaşılır |
| Temperature açıklaması | Slider altında "Düşük: tutarlı · Yüksek: yaratıcı" | Teknik olmayan kullanıcı da anlar |
| Yükleniyor göstergesi | Cevap akışla (streaming) gelir; ilk parça gelene kadar `st.spinner("Düşünüyorum...")` gösterilir | Bekleme hissini azaltır |
| Karakter sınırı | `st.chat_input(max_chars=1000)` | Sınır kullanıcıya görünür |
| Sorumluluk uyarısı | Kenar çubuğunun altında sabit uyarı (bkz. [08-etik.md](08-etik.md)) | Yanlış bilgi riskine karşı şeffaflık |
| Mod değişikliği | Geçmiş silinirken `st.toast("Mod değişti, yeni sohbet başladı")` gösterilir | Geçmişin neden kaybolduğu anlaşılır |
| Geri bildirim | Her cevabın altında 👍/👎; kenar çubuğunda oturum özeti | Kullanıcı memnuniyeti ölçülür, demoda gösterilir (FR-14) |
| Yanıt bilgisi | Cevabın altında küçük gri yazıyla süre ve token | Şeffaflık; performans gözlemlenir (FR-15) |
| Yedek model notu | Yedek model kullanıldıysa cevabın altında bilgi notu | Kullanıcı hangi modelin cevap verdiğini bilir (FR-16) |

### 4.3 Hata ve uyarı mesajları

| Durum | Mesaj |
|---|---|
| Boş mesaj | (Gönderilmez, mesaj yok) |
| Uzun mesaj | "Mesajın en fazla 1000 karakter olabilir." |
| Hız sınırı | "Çok hızlı mesaj gönderiyorsun. Lütfen bir dakika bekle." |
| API anahtarı geçersiz/eksik | "Asistana şu anda ulaşılamıyor. Lütfen yöneticiye bildir." |
| Zaman aşımı / ağ hatası | "Cevap zamanında gelmedi. Lütfen tekrar dene." |
| Kota aşıldı | "Kullanım sınırına ulaşıldı. Lütfen daha sonra tekrar dene." |

### 4.4 Örnek soru butonları

| Mod | Örnekler |
|---|---|
| Kurallar & Taktik | Ofsayt nedir? · VAR ne zaman devreye girer? · 4-3-3'ün güçlü ve zayıf yanları |
| Türk Futbolu | 2002 Dünya Kupası macerası · Galatasaray'ın UEFA Kupası zaferi · Süper Lig'in en çok şampiyon olan kulübü |
| Dünya Futbolu | En çok Dünya Kupası kazanan ülke · Total futbol nedir? · Arsenal'in yenilmezler sezonu |

## 5. Veri Modelleri

**Sohbet mesajı**
```json
{"role": "user", "content": "Ofsayt nedir?"}
```

**Test sonucu satırı**
```json
{
  "id": "KT-01",
  "mode": "kurallar_taktik",
  "question": "...",
  "expected": "...",
  "run": 1,
  "answer": "...",
  "latency_s": 2.4,
  "first_token_s": 0.6,
  "prompt_tokens": 512,
  "completion_tokens": 340,
  "tokens_estimated": false,
  "model": "deepseek-v4.1-flash-free",
  "used_fallback": false,
  "error": null,
  "temperature": 0.3,
  "prompt_version": "v1",
  "dogruluk": null,
  "tutarlilik": null,
  "kullanislilik": null,
  "davranis": null
}
```

## 6. LLM Seçimi

| | |
|---|---|
| **Model** | DeepSeek V4.1 Flash (`deepseek-v4.1-flash-free`) |
| **Sağlayıcı** | OpenCode Go |
| **API** | OpenAI uyumlu (`openai` Python SDK, `base_url` ile) |
### Seçim kriterleri ve gerekçe

| Kriter | Neden önemli | DeepSeek V4.1 Flash (OpenCode Go) |
|---|---|---|
| **Maliyet** | Öğrenci projesi; testlerde yüzlerce istek atılacak (49 soru × 3 tekrar × 3 prompt sürümü × 3 model × birden fazla temperature) | Mevcut OpenCode Go aboneliğine dahil; ek ücret yok |
| **Hız** | Sohbet arayüzünde ilk cevap < 10 sn hedefi (H6) | "Flash" sınıfı, düşük gecikme için tasarlanmış küçük/hızlı model |
| **Entegrasyon** | Basit ve değiştirilebilir kod (NFR-04) | OpenAI uyumlu API: `openai` SDK ile yalnızca `base_url` değişiyor; streaming destekli |
| **Bağlam penceresi** | Çok turlu sohbet geçmişi + sistem promptu | Geniş bağlam penceresi (kaynaklarda 1M token belirtiliyor); projenin ihtiyacının çok üzerinde |
| **Açıklık** | Şeffaflık, sorumlu AI | Model ağırlıkları açık lisansla (MIT) yayımlanmış |
| **Türkçe kalitesi** | Tüm arayüz ve cevaplar Türkçe (NFR-01) | ⏳ Kendi testlerimizle ölçülecek (bkz. 04 – doğruluk ve kullanışlılık puanları) |

### Alternatiflerle karşılaştırma

| | DeepSeek V4.1 Flash (OpenCode Go) | OpenAI GPT | Google Gemini | Anthropic Claude |
|---|---|---|---|---|
| Ek maliyet | Yok (mevcut abonelik) | Kullandıkça öde | Sınırlı ücretsiz katman, sonra ücretli | Kullandıkça öde |
| OpenAI uyumlu API | ✅ | ✅ (kendisi) | Kısmen (uyumluluk katmanı) | Kendi SDK'sı |
| Hesap/anahtar hazır mı | ✅ | ❌ | ❌ | ❌ |

**Ön seçim:** Proje "temel düzey" bir LLM kullanımı gerektirdiğinden belirleyici kriterler maliyet, kolay entegrasyon ve hızdır. DeepSeek V4.1 Flash bu üç kriteri de karşıladığı için başlangıçta ana model olarak seçildi.

### Ölçüme dayalı son karar

Ön seçim, OpenCode Go üzerindeki 3 modelin aynı test setiyle karşılaştırılmasıyla doğrulanır (bkz. [04-test-plani.md](04-test-plani.md), Bölüm 8). Tüm modeller aynı OpenAI uyumlu API'den çağrıldığı için model değiştirmek yalnızca `LLM_MODEL` değerini değiştirmek demek.

| Rol | Model | Gerekçe (ölçüm sonrası doldurulacak) |
|---|---|---|
| Ana model (`LLM_MODEL`) | [karşılaştırma sonrası] | |
| Yedek model (`LLM_FALLBACK_MODEL`) | [karşılaştırma sonrası] | |

> Not: Fiyat ve ücretsiz katman bilgileri sık değişir. Rapor yazılırken sağlayıcıların güncel sayfalarından kontrol edilmeli.

**`requirements.txt` (taslak):** `streamlit`, `openai`, `python-dotenv`
