#!/usr/bin/env python3
"""Generate romaji readings for every example sentence.

Requires: python3 -m pip install --user pykakasi
Output: data/ja-romaji.json, consumed by build_ja_atlas.py.
"""

import json
import re
import sys
from pathlib import Path

import pykakasi

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
SOURCE = DATA / "word-atlas-ja.json"
TARGET = DATA / "ja-romaji.json"

KEEP = re.compile(r"[^a-z0-9 ]")


def to_romaji(kakasi, sentence):
    chunks = []
    for item in kakasi.convert(sentence):
        value = item["hepburn"].lower()
        value = KEEP.sub(" ", value)
        value = re.sub(r"\s+", " ", value).strip()
        if value:
            chunks.append(value)
    return " ".join(chunks)


def main():
    entries = json.loads(SOURCE.read_text(encoding="utf-8"))
    kakasi = pykakasi.kakasi()
    result = {}
    for e in entries:
        readings = [to_romaji(kakasi, x["en"]) for x in e["ex"]]
        if not all(readings):
            raise ValueError(f"empty romaji reading for {e['id']}")
        result[e["id"]] = readings
    TARGET.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"romaji for {len(result)} entries -> {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
