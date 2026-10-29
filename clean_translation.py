"""Translate FMSG from the game's original English files.

No fan-translated FMSG files are read by this program. Translation entries
are keyed by file/index and guarded by a SHA256 of the *English* source.
Builds are drafts until coverage and in-game font/layout tests are complete.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
import re

from fmsg_format import GAME, ROOT, load, pack, tags

SOURCE = GAME / "binary" / "text" / "USen"
TRANSLATIONS = ROOT / "translations_from_english.json"
REVIEW = ROOT / "work" / "english_source.jsonl"
OUTPUT = ROOT / "out" / "clean_es_draft" / "binary" / "text" / "USen"
QA = ROOT / "work" / "clean_es_qa.json"

# Spanish accented capitals and inverted punctuation are available in the
# separately generated draft G1N atlas; unsupported symbols remain blocked.
# Runtime glyph rendering is still unverified: never install this draft yet.
UNSUPPORTED = set("«»ªº")
# Keep the text in correct Unicode in the intermediate draft.
CODE = re.compile(r"\^[0-9a-fA-F]{2}(?:~[0-9a-fA-F]{2}~)?|%(?:\d+\$)?[-+ .#0-9]*[a-zA-Z]")
JAPANESE = re.compile(r"[\u3040-\u9fff]")


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def source_files():
    found = sorted(SOURCE.glob("*.fmsg"))
    if len(found) != 13:
        raise ValueError(f"Expected 13 English FMSG files, found {len(found)}")
    for path in found:
        yield path, load(path)


def load_edits() -> dict[tuple[str, int], dict]:
    entries = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))
    result = {}
    for item in entries:
        key = (item["file"], item["index"])
        if key in result:
            raise ValueError(f"Duplicate translation: {key}")
        if not isinstance(item["es"], str) or not item["es"].strip():
            raise ValueError(f"Missing Spanish text: {key}")
        result[key] = item
    return result


def export():
    REVIEW.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with REVIEW.open("w", encoding="utf-8", newline="\n") as fd:
        for path, parsed in source_files():
            for index, en in enumerate(parsed.strings):
                fd.write(json.dumps({
                    "file": path.name, "index": index,
                    "english": en, "source_sha256": digest(en),
                }, ensure_ascii=False) + "\n")
                total += 1
    print(f"Exported {total} English source entries to {REVIEW}")


def build():
    entries = load_edits()
    seen = set()
    total = changed = words_to_translate = 0
    warnings = collections.Counter()
    examples = collections.defaultdict(list)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path, en in source_files():
        strings = list(en.strings)
        for index, source in enumerate(strings):
            total += 1
            key = (path.name, index)
            entry = entries.get(key)
            if entry is None:
                if source.strip() and not JAPANESE.search(source) and not set(source) <= set("■▼\t\r\n "):
                    words_to_translate += 1
                    if len(examples["untranslated"]) < 20:
                        examples["untranslated"].append(f"{path.name}#{index}")
                continue
            if digest(source) != entry["source_sha256"]:
                raise ValueError(f"English baseline mismatch: {path.name}#{index}")
            translated = entry["es"]
            if "\x00" in translated or "\r" in translated:
                raise ValueError(f"Embedded CR/NUL: {key}")
            if tags(source) != tags(translated):
                raise ValueError(f"Control/format codes changed: {key}\nEN: {tags(source)}\nES: {tags(translated)}")
            if CODE.findall(source) != CODE.findall(translated):
                raise ValueError(f"Control/format code order changed: {key}")
            if unsupported := UNSUPPORTED.intersection(translated):
                raise ValueError(f"Unverified characters {unsupported}: {key}")
            if translated == source:
                warnings["same_as_source"] += 1
            if len(translated) > 1.7 * len(source) and len(source) > 30:
                warnings["length_70pct_greater"] += 1
                if len(examples["length_70pct_greater"]) < 20:
                    examples["length_70pct_greater"].append(f"{path.name}#{index}")
            strings[index] = translated
            changed += 1
            seen.add(key)
        target = OUTPUT / path.name
        target.write_bytes(pack(en, strings))
        if load(target).strings != tuple(strings):
            raise ValueError(f"Readback mismatch: {target}")
        # Original entries not edited must roundtrip identically.
        if all((path.name, i) not in entries for i in range(len(strings))):
            if target.read_bytes() != path.read_bytes():
                raise ValueError(f"Unmodified file changed: {path.name}")
    if set(entries) != seen:
        raise ValueError(f"Translations reference unknown entries: {set(entries)-seen}")
    report = {
        "status": "DRAFT - do not install; incomplete translation and glyph QA",
        "reference": "original English USen FMSG only",
        "total_entries": total, "translated_entries": changed,
        "untranslated_or_unreviewed_entries": words_to_translate,
        "warnings": dict(warnings), "examples": dict(examples),
        "output": str(OUTPUT),
        "font_status": "Original game font remains in place; Spanish glyphs not yet verified",
    }
    QA.parent.mkdir(parents=True, exist_ok=True)
    QA.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("export", "build"))
    action = parser.parse_args().action
    {"export": export, "build": build}[action]()
