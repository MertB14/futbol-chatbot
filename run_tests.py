"""Otomatik test scripti (FR-10, FR-13, FR-16, FR-17).

Örnekler:
    python run_tests.py
    python run_tests.py --mode turk_futbolu
    python run_tests.py --ids KT-01,DV-01 --repeat 1
    python run_tests.py --temperature 0.8
    python run_tests.py --prompt-version v0
    python run_tests.py --models model-a,model-b,model-c --blind
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import string
import sys
import time
from datetime import datetime
from pathlib import Path

import config
import llm_client
import security
from prompt_loader import available_versions, load_system_prompt

QUESTIONS_FILE = config.TESTS_DIR / "test_questions.json"
RESULTS_DIR = config.TESTS_DIR / "results"

RESULT_FIELDS = [
    "id", "mode", "category", "question", "expected", "depends_on", "paraphrase_of",
    "run", "answer", "latency_s", "first_token_s", "prompt_tokens", "completion_tokens",
    "tokens_estimated", "model", "used_fallback", "error", "temperature", "prompt_version",
    "dogruluk", "tutarlilik", "kullanislilik", "davranis", "not",
]
SCORE_FIELDS = ["dogruluk", "tutarlilik", "kullanislilik", "davranis", "not"]
BLIND_FIELDS = ["sira", "id", "category", "question", "expected", "run", "kod", "answer"] + SCORE_FIELDS


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Futbol Asistanı test scripti")
    p.add_argument("--mode", choices=list(config.MODES), help="Yalnızca bu moddaki soruları çalıştır")
    p.add_argument("--ids", help="Virgülle ayrılmış soru ID'leri (ör. KT-01,DV-01)")
    p.add_argument("--repeat", type=int, default=3, help="Her sorunun tekrar sayısı (varsayılan 3)")
    p.add_argument("--temperature", type=float, default=config.TEMPERATURE_DEFAULT)
    p.add_argument("--prompt-version", default="v1", help="Prompt sürümü (v0, v1, v2...)")
    p.add_argument("--delay", type=float, default=1.0, help="İstekler arası bekleme, sn (SEC-14)")
    p.add_argument("--model", help="Tek bir modelle çalıştır (varsayılan LLM_MODEL)")
    p.add_argument(
        "--models", nargs="?", const="", default=None,
        help="Virgülle ayrılmış model listesi; değer verilmezse LLM_COMPARE_MODELS kullanılır",
    )
    p.add_argument("--use-fallback", action="store_true", help="Yedek modeli aç (varsayılan kapalı)")
    p.add_argument("--blind", action="store_true", help="Kör puanlama dosyası üret")
    return p.parse_args()


def load_questions() -> list[dict]:
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        return json.load(f)


def select_questions(all_q: list[dict], mode: str | None, ids: str | None) -> list[dict]:
    """Filtreler ve çok turlu soruların bağımlılıklarını otomatik ekler."""
    by_id = {q["id"]: q for q in all_q}
    if ids:
        wanted = {x.strip() for x in ids.split(",") if x.strip()}
        unknown = wanted - by_id.keys()
        if unknown:
            sys.exit(f"Bilinmeyen soru ID'leri: {', '.join(sorted(unknown))}")
    else:
        wanted = set(by_id)
    if mode:
        wanted = {i for i in wanted if by_id[i]["mode"] == mode}

    # Bağımlılıkları ekle (cok_turlu)
    stack = list(wanted)
    while stack:
        dep = by_id[stack.pop()].get("depends_on")
        if dep and dep not in wanted:
            wanted.add(dep)
            stack.append(dep)

    # Dosyadaki sıra korunur; bağımlılıklar dosyada önce geldiği için önce çalışır
    return [q for q in all_q if q["id"] in wanted]


def resolve_models(args: argparse.Namespace) -> list[str]:
    if args.models is not None:
        models = [m.strip() for m in args.models.split(",") if m.strip()] or config.env_list(
            "LLM_COMPARE_MODELS"
        )
        if not models:
            sys.exit("Model listesi boş. --models a,b,c verin ya da .env içinde LLM_COMPARE_MODELS tanımlayın.")
        return models
    return [args.model or llm_client.default_model()]


def run_one(q: dict, model: str, run: int, args, answers: dict) -> dict:
    """Tek bir soruyu çalıştırır ve sonuç satırını döner."""
    row = {f: None for f in RESULT_FIELDS}
    row.update(
        id=q["id"], mode=q["mode"], category=q["category"], question=q["question"],
        expected=q.get("expected"), depends_on=q.get("depends_on"),
        paraphrase_of=q.get("paraphrase_of"), run=run, model=model,
        temperature=llm_client.clamp_temperature(args.temperature),
        prompt_version=args.prompt_version, used_fallback=False,
    )

    history: list[dict] = []
    dep = q.get("depends_on")
    if dep:
        dep_answer = answers.get((model, dep, run))
        if dep_answer is None:
            row["error"] = f"Bağımlı soru ({dep}) cevaplanamadı"
            return row
        history += [
            {"role": "user", "content": dep_answer[0]},
            {"role": "assistant", "content": dep_answer[1]},
        ]

    ok, cleaned = security.validate_input(q["question"])
    if not ok:
        row["error"] = cleaned or "Boş soru"
        return row
    history.append({"role": "user", "content": cleaned})

    try:
        res = llm_client.chat(
            load_system_prompt(q["mode"], args.prompt_version),
            security.build_api_messages(history, config.MAX_HISTORY),
            temperature=args.temperature,
            model=model,
            use_fallback=args.use_fallback,
        )
    except llm_client.LLMError as exc:
        row["error"] = f"{exc.kind}: {exc.detail}"[:500]
        return row

    row.update(
        answer=res.text, latency_s=res.latency_s, first_token_s=res.first_token_s,
        prompt_tokens=res.prompt_tokens, completion_tokens=res.completion_tokens,
        tokens_estimated=res.tokens_estimated, model=res.model, used_fallback=res.used_fallback,
    )
    answers[(model, q["id"], run)] = (cleaned, res.text)
    return row


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    # utf-8-sig: Excel Türkçe karakterleri doğru açsın
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_blind(stamp: str, rows: list[dict], models: list[str]) -> tuple[Path, Path]:
    """Kör puanlama: karışık sıra, model adı yerine A/B/C kodu (04, Bölüm 8.2)."""
    codes = list(string.ascii_uppercase[: len(models)])
    random.shuffle(codes)
    key = dict(zip(models, codes))
    blind_rows = []
    for r in rows:
        if r["error"]:
            continue
        b = {f: r.get(f) for f in BLIND_FIELDS}
        b["kod"] = key[r["requested_model"]]
        blind_rows.append(b)
    random.shuffle(blind_rows)
    for n, b in enumerate(blind_rows, 1):
        b["sira"] = n

    blind_path = RESULTS_DIR / f"blind_{stamp}.csv"
    key_path = RESULTS_DIR / f"blind_key_{stamp}.json"
    write_csv(blind_path, blind_rows, BLIND_FIELDS)
    with open(key_path, "w", encoding="utf-8") as f:
        json.dump({code: model for model, code in key.items()}, f, ensure_ascii=False, indent=2)
    return blind_path, key_path


def print_summary(rows: list[dict], models: list[str]) -> None:
    print("\n=== Özet ===")
    print(f"{'Model':<40} {'Soru':>5} {'Hata':>5} {'Ort. süre':>10} {'Ort. ilk parça':>15} {'Ort. çıktı token':>17}")
    for m in models:
        mr = [r for r in rows if r["requested_model"] == m]
        ok = [r for r in mr if not r["error"]]
        avg = lambda key: (sum(r[key] for r in ok if r[key] is not None) / max(1, sum(1 for r in ok if r[key] is not None)))  # noqa: E731
        print(
            f"{m:<40} {len(mr):>5} {len(mr) - len(ok):>5} "
            f"{avg('latency_s'):>9.2f}s {avg('first_token_s'):>14.2f}s {avg('completion_tokens'):>17.0f}"
        )


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    args = parse_args()
    if args.prompt_version not in available_versions():
        sys.exit(f"Prompt sürümü bulunamadı: {args.prompt_version} (mevcut: {', '.join(available_versions())})")
    if args.repeat < 1:
        sys.exit("--repeat en az 1 olmalı")

    questions = select_questions(load_questions(), args.mode, args.ids)
    models = resolve_models(args)
    total = len(questions) * args.repeat * len(models)
    print(
        f"{len(questions)} soru × {args.repeat} tekrar × {len(models)} model = {total} istek "
        f"| prompt {args.prompt_version} | temperature {llm_client.clamp_temperature(args.temperature)} "
        f"| yedek model {'açık' if args.use_fallback else 'kapalı'}"
    )

    rows: list[dict] = []
    answers: dict = {}
    n = 0
    for model in models:
        for q in questions:
            for run in range(1, args.repeat + 1):
                n += 1
                row = run_one(q, model, run, args, answers)
                row["requested_model"] = model
                rows.append(row)
                status = f"HATA ({row['error'][:60]})" if row["error"] else f"{row['latency_s']:.1f}s"
                print(f"[{n}/{total}] {model} {q['id']} #{run}: {status}", flush=True)
                if n < total and args.delay > 0:
                    time.sleep(args.delay)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = RESULTS_DIR / f"results_{stamp}.json"
    csv_path = RESULTS_DIR / f"results_{stamp}.csv"
    meta = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "prompt_version": args.prompt_version,
        "temperature": llm_client.clamp_temperature(args.temperature),
        "repeat": args.repeat,
        "models": models,
        "use_fallback": args.use_fallback,
        "max_tokens": config.MAX_TOKENS,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "results": rows}, f, ensure_ascii=False, indent=2)
    write_csv(csv_path, rows, RESULT_FIELDS)
    print(f"\nSonuçlar: {json_path}\n          {csv_path}")

    if args.blind:
        blind_path, key_path = write_blind(stamp, rows, models)
        print(f"Kör puanlama: {blind_path}\nAnahtar (puanlamadan sonra aç): {key_path}")

    print_summary(rows, models)


if __name__ == "__main__":
    main()
