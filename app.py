"""Futbol Asistanı – Streamlit arayüzü.

Çalıştırma: streamlit run app.py
"""

import logging
import os
import time
import uuid

import streamlit as st

import config
import llm_client
import security
from prompt_loader import load_system_prompt

logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

st.set_page_config(page_title="Futbol Asistanı", page_icon="⚽", layout="centered")


# --- st.secrets desteği (NFR-03): .env yoksa Streamlit secrets'tan oku ---
def _load_streamlit_secrets() -> None:
    try:
        secrets = dict(st.secrets)
    except Exception:  # secrets.toml yoksa hata verir
        return
    for name in ("OPENCODE_API_KEY", "LLM_BASE_URL", "LLM_MODEL", "LLM_FALLBACK_MODEL", "LLM_MODELS", "LLM_REASONING_EFFORT"):
        if name in secrets and not os.environ.get(name):
            os.environ[name] = str(secrets[name])


_load_streamlit_secrets()

MODEL_OPTIONS = config.available_models()  # Seçilebilir modeller (izin listesi)


# --- Oturum durumu ---
def _init_state() -> None:
    defaults = {
        "messages": [],  # [{"role", "content", "meta"?}]
        "mode": config.DEFAULT_MODE,
        "temperature": config.TEMPERATURE_DEFAULT,
        "model": MODEL_OPTIONS[0],
        "request_times": [],
        "chat_id": 0,  # Sohbet temizlenince artar; geri bildirim anahtarlarını sıfırlar
        "session_id": str(uuid.uuid4()),  # Sağlayıcıya giden sohbet kimliği
        "toast": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _reset_chat() -> None:
    st.session_state.messages = []
    st.session_state.chat_id += 1
    st.session_state.session_id = str(uuid.uuid4())


def _on_mode_change() -> None:  # FR-06
    _reset_chat()
    st.session_state.toast = "Mod değişti, yeni sohbet başladı"


def _on_clear() -> None:  # FR-05
    _reset_chat()
    st.session_state.toast = "Sohbet temizlendi"


def _feedback_key(i: int) -> str:
    return f"fb_{st.session_state.chat_id}_{i}"


def _feedback_summary() -> tuple[int, int]:
    """Oturumdaki 👍/👎 sayıları (FR-14). Yalnızca bellekte tutulur (ETK-02)."""
    up = down = 0
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] != "assistant":
            continue
        value = st.session_state.get(_feedback_key(i))
        if value == 1:
            up += 1
        elif value == 0:
            down += 1
    return up, down


def _meta_caption(meta: dict) -> str:
    """'2.1 sn · giriş 512 · çıkış 340 token' (FR-15). Tahminse '~' eklenir."""
    approx = "~" if meta.get("tokens_estimated") else ""
    parts = [f"{meta['latency_s']:.1f} sn"]
    if meta.get("prompt_tokens") is not None:
        parts.append(f"giriş {approx}{meta['prompt_tokens']}")
    if meta.get("completion_tokens") is not None:
        parts.append(f"çıkış {approx}{meta['completion_tokens']} token")
    return " · ".join(parts)


def _render_assistant_meta(i: int, meta: dict) -> None:
    st.caption(_meta_caption(meta))
    if meta.get("used_fallback"):
        st.caption("ℹ️ Ana model yanıt vermediği için yedek model kullanıldı.")  # FR-16
    if meta.get("truncated"):
        st.caption("✂️ Cevap uzunluk sınırına ulaştığı için kesildi. Soruyu daraltmayı dene.")
    st.feedback("thumbs", key=_feedback_key(i))


_init_state()

# .env değişip seçili model listeden çıktıysa varsayılana dön
if st.session_state.model not in MODEL_OPTIONS:
    st.session_state.model = MODEL_OPTIONS[0]

if st.session_state.toast:
    st.toast(st.session_state.toast)
    st.session_state.toast = None


# --- Kenar çubuğu ---
with st.sidebar:
    st.header("⚽ Futbol Asistanı")

    st.radio(
        "Konu modu",
        options=list(config.MODES),
        format_func=config.MODES.get,
        key="mode",
        on_change=_on_mode_change,
    )
    st.caption(config.MODE_DESCRIPTIONS[st.session_state.mode])

    st.slider(
        "Temperature",
        min_value=config.TEMPERATURE_MIN,
        max_value=config.TEMPERATURE_MAX,
        step=config.TEMPERATURE_STEP,
        key="temperature",
    )
    st.caption("Düşük: daha tutarlı · Yüksek: daha yaratıcı")

    st.selectbox(
        "AI modeli",
        options=MODEL_OPTIONS,
        key="model",
        disabled=len(MODEL_OPTIONS) < 2,
        help="Liste .env dosyasındaki LLM_MODELS değişkeninden gelir.",
    )

    up, down = _feedback_summary()
    st.markdown(f"**Bu oturum:** 👍 {up} · 👎 {down}")
    last_meta = next(
        (m["meta"] for m in reversed(st.session_state.messages) if m.get("meta")), None
    )
    if last_meta:
        st.caption(f"Son cevabın modeli: `{last_meta['model']}`")

    st.button("🗑️ Sohbeti Temizle", on_click=_on_clear, width="stretch")

    st.divider()
    st.info(config.DISCLAIMER, icon="ℹ️")  # ETK-08
    st.caption(config.PRIVACY_NOTICE)  # ETK-01


# --- Ana alan ---
mode = st.session_state.mode
st.title("⚽ Futbol Asistanı")
st.caption(f"Mod: {config.MODES[mode]}")

clicked_example = None
if not st.session_state.messages:
    # Karşılama mesajı modele gönderilmez (06-mimari.md, Bölüm 4.2)
    with st.chat_message("assistant"):
        st.markdown(config.WELCOME_MESSAGES[mode])
        st.markdown("**Örnek sorular:**")
        cols = st.columns(len(config.EXAMPLE_QUESTIONS[mode]))
        for j, (col, q) in enumerate(zip(cols, config.EXAMPLE_QUESTIONS[mode])):
            if col.button(q, key=f"ex_{mode}_{j}", width="stretch"):
                clicked_example = q

# Geçmiş mesajlar (HTML kapalı, SEC-15)
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("meta"):
            _render_assistant_meta(i, msg["meta"])

typed = st.chat_input("Futbolla ilgili sorunu yaz...", max_chars=config.MAX_INPUT_CHARS)
raw_question = typed if typed is not None else clicked_example

if raw_question is not None:
    ok, result = security.validate_input(raw_question)
    if not ok:
        if result:  # Boş mesajda uyarı gösterilmez
            st.warning(result)
    elif not security.check_rate_limit(st.session_state.request_times):
        st.warning("Çok hızlı mesaj gönderiyorsun. Lütfen bir dakika bekle.")
    else:
        question = result
        st.session_state.request_times.append(time.time())
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("_Düşünüyorum..._")
            streamed: list[str] = []

            def on_token(piece: str) -> None:
                streamed.append(piece)
                placeholder.markdown("".join(streamed) + "▌")

            try:
                system_prompt = load_system_prompt(mode, config.PROMPT_VERSION)
                api_messages = security.build_api_messages(
                    st.session_state.messages, config.MAX_HISTORY
                )
                res = llm_client.chat(
                    system_prompt,
                    api_messages,
                    temperature=st.session_state.temperature,
                    model=st.session_state.model,
                    on_token=on_token,
                    session_id=st.session_state.session_id,
                )
            except llm_client.LLMError as exc:
                placeholder.empty()
                st.error(exc.user_message)  # FR-11, SEC-16
                st.session_state.messages.pop()  # Cevapsız soruyu geçmişte bırakma
            else:
                answer = res.text.strip() or "Bu soruya şu anda bir cevap üretemedim. Lütfen tekrar dene."
                placeholder.markdown(answer)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "meta": {
                            "model": res.model,
                            "used_fallback": res.used_fallback,
                            "latency_s": res.latency_s,
                            "first_token_s": res.first_token_s,
                            "prompt_tokens": res.prompt_tokens,
                            "completion_tokens": res.completion_tokens,
                            "tokens_estimated": res.tokens_estimated,
                            "truncated": res.truncated,
                        },
                    }
                )
                st.rerun()  # Geri bildirim butonları ve kenar çubuğu özeti için yeniden çiz
