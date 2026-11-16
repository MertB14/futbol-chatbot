"""Sistem promptunu dosyalardan yükler: <sürüm>/base.md + <sürüm>/<mod>.md (NFR-05)."""

import re
from functools import lru_cache

from config import MODES, PROMPTS_DIR

_VERSION_RE = re.compile(r"^v\d+$")


def available_versions() -> list[str]:
    """prompts/ altındaki sürüm klasörlerini döner (ör. ['v0', 'v1'])."""
    return sorted(
        p.name for p in PROMPTS_DIR.iterdir() if p.is_dir() and _VERSION_RE.match(p.name)
    )


@lru_cache(maxsize=32)
def load_system_prompt(mode: str, version: str) -> str:
    """Seçili mod ve sürüm için sistem promptunu döner.

    Sürümde mod dosyası yoksa (ör. v0) yalnızca base.md kullanılır.
    """
    if mode not in MODES:
        raise ValueError(f"Bilinmeyen mod: {mode}")
    if not _VERSION_RE.match(version):
        raise ValueError(f"Geçersiz prompt sürümü: {version}")

    version_dir = PROMPTS_DIR / version
    base_file = version_dir / "base.md"
    if not base_file.is_file():
        raise FileNotFoundError(f"Prompt bulunamadı: {base_file}")

    parts = [base_file.read_text(encoding="utf-8").strip()]
    mode_file = version_dir / f"{mode}.md"
    if mode_file.is_file():
        parts.append(mode_file.read_text(encoding="utf-8").strip())
    return "\n\n".join(parts)
