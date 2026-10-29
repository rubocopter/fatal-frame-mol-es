"""Create independently sourced, *unreviewed* ES candidates for missing USen strings.

This writes only under work/. Neither the finished translation dictionary nor
the installed game is modified. Every output must be edited/reviewed before use.

Usage: python -X utf8 machine_candidates.py [--file text8.fmsg] [--workers 4]
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import threading
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

from clean_translation import CODE, JAPANESE, ROOT, UNSUPPORTED, digest
from fmsg_format import tags

SOURCE = ROOT / "work" / "english_source.jsonl"
EDITED = ROOT / "translations_from_english.json"
OUTPUT = ROOT / "work" / "machine_candidates.jsonl"
CACHE = ROOT / "work" / "machine_cache.json"
REPORT = ROOT / "work" / "machine_candidates_qa.json"
EXCLUDED_FILES = {"system.fmsg", "system2.fmsg", "textnew_02.fmsg"}
TRANSLATABLE = re.compile(r"[A-Za-z]{2}")
lock = threading.Lock()


def translate_online(text: str) -> str:
    query = urllib.parse.urlencode({"client": "gtx", "sl": "en", "tl": "es", "dt": "t", "q": text})
    request = urllib.request.Request(
        "https://translate.googleapis.com/translate_a/single?" + query,
        headers={"User-Agent": "Mozilla/5.0 (compatible; local-game-translation-prototype)"},
    )
    last_error = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.load(response)
            translated = "".join(fragment[0] or "" for fragment in result[0])
            if not translated:
                raise ValueError("Empty translation")
            return translated
        except Exception as e:
            last_error = e
            time.sleep(0.5 * 2**attempt)
    raise RuntimeError(f"Translation service failed: {last_error}")


def translate_piece(src: str, cache: dict[str, str]) -> str:
    # Control tokens and printf-style placeholders must be preserved exactly.
    # Translating around a token can change grammar, requiring manual review.
    pieces = CODE.split(src)
    codes = CODE.findall(src)
    out = []
    for index, part in enumerate(pieces):
        if TRANSLATABLE.search(part):
            with lock:
                trans = cache.get(part)
            if trans is None:
                trans = translate_online(part)
                with lock:
                    cache[part] = trans
            out.append(trans)
        else:
            out.append(part)
        if index < len(codes):
            out.append(codes[index])
    return "".join(out)


def translate_one(row: dict, cache: dict[str, str]) -> dict:
    src = row["english"]
    try:
        es = translate_piece(src, cache)
        # The game uses a private font with deliberately limited glyph coverage.
        es = es.replace("«", '"').replace("»", '"').replace("ª", "a").replace("º", "o")
        if CODE.findall(src) != CODE.findall(es) or tags(src) != tags(es):
            return {**row, "candidate": es, "status": "invalid_tags"}
        if any(c in es for c in UNSUPPORTED):
            return {**row, "candidate": es, "status": "unsupported"}
        if not es.strip() or es.strip() == src.strip():
            return {**row, "candidate": es, "status": "unchanged"}
        return {**row, "candidate": es, "status": "unreviewed"}
    except Exception as e:
        return {**row, "candidate": None, "status": "error", "error": str(e)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Limit to one FMSG file")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    authored = {(r["file"], r["index"]) for r in json.loads(EDITED.read_text(encoding="utf-8"))}
    rows = [json.loads(s) for s in SOURCE.read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if (r["file"], r["index"]) not in authored
            and r["file"] not in EXCLUDED_FILES
            and (args.file is None or r["file"] == args.file)
            and TRANSLATABLE.search(r["english"])
            and not JAPANESE.search(r["english"])
            and not ("▼" in r["english"] or "■" in r["english"])]
    prior = {}
    if OUTPUT.exists():
        prior = {(r["file"], r["index"]): r for r in map(json.loads, OUTPUT.read_text(encoding="utf-8").splitlines())}
    pending = [r for r in rows if (r["file"], r["index"]) not in prior]
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    print(f"Candidates already stored: {len(prior)}; pending: {len(pending)}", flush=True)

    def persist() -> None:
        # Stable source order, resumable even if the online service fails later.
        tmp = OUTPUT.with_suffix(".jsonl.tmp")
        tmp.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in sorted(prior.values(), key=lambda r: (r["file"], r["index"]))) + "\n", encoding="utf-8")
        tmp.replace(OUTPUT)
        tmp = CACHE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(CACHE)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(translate_one, r, cache) for r in pending]
        for n, job in enumerate(concurrent.futures.as_completed(jobs), 1):
            result = job.result()
            prior[(result["file"], result["index"])] = result
            if n % 50 == 0 or n == len(pending):
                persist()
                counts = Counter(r["status"] for r in prior.values())
                print(f"Progress {n}/{len(pending)}; {dict(counts)}", flush=True)
    REPORT.write_text(json.dumps({"purpose": "Draft candidates only; linguistic review required",
                                  "total": len(prior), "status_counts": Counter(r["status"] for r in prior.values()),
                                  "source": "game original English USen FMSG, external automatic translation"},
                                 ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
