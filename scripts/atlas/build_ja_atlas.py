#!/usr/bin/env python3
"""Build the Japanese atlas dataset from the hand-curated lexicon.

Source of truth: data/ja-lexicon.txt (pipe separated, 18 columns).
Outputs: data/*.json, data/*.csv, public/atlas/index.json, public/atlas/entries/*.json
"""

import csv
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEXICON = ROOT / "data" / "ja-lexicon.txt"
DATA = ROOT / "data"
ROMAJI = DATA / "ja-romaji.json"
ATLAS = ROOT / "public" / "atlas"

LEVELS = ["N5", "N4", "N3", "N2", "N1"]
TOPICS = [
    ["education", "教育"],
    ["work", "职场"],
    ["technology", "科技"],
    ["science", "科学"],
    ["environment", "环境"],
    ["health", "健康"],
    ["society", "社会"],
    ["government", "政法"],
    ["economy", "经济"],
    ["media", "媒体"],
    ["arts", "艺术"],
    ["travel", "旅行"],
    ["city", "城市"],
    ["nature", "自然"],
    ["daily", "生活"],
    ["emotion", "情感"],
    ["thinking", "思维"],
    ["sport", "运动"],
    ["history", "历史"],
]
TOPIC_KEYS = [t[0] for t in TOPICS]
CHUNK = 100
MEDIA_ALL = 31
COLUMNS = 18
ID_RE = re.compile(r"^[a-z0-9-]{1,64}$")


def read_lexicon():
    text = LEXICON.read_text(encoding="utf-8")
    rows = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) != COLUMNS:
            raise ValueError(f"lexicon line {lineno}: expected {COLUMNS} columns, got {len(parts)}: {line[:80]}")
        rows.append((lineno, [p.strip() for p in parts]))
    if not rows:
        raise ValueError("lexicon is empty")
    return rows


def split_list(value):
    return [s.strip() for s in value.split(";") if s.strip()]


def build():
    rows = read_lexicon()
    romaji_table = json.loads(ROMAJI.read_text(encoding="utf-8"))
    entries = []
    seen = set()
    for lineno, c in rows:
        (
            id_, w, kana, romaji, pos, zh, ja, level, topic,
            ex1ja, ex1zh, ex2ja, ex2zh, col, fam, syn, ant, tip,
        ) = c
        if not ID_RE.match(id_):
            raise ValueError(f"line {lineno}: invalid id {id_!r}")
        if id_ in seen:
            raise ValueError(f"line {lineno}: duplicate id {id_}")
        seen.add(id_)
        for name, value in (("w", w), ("kana", kana), ("romaji", romaji), ("pos", pos), ("zh", zh), ("ex1ja", ex1ja), ("ex1zh", ex1zh)):
            if not value:
                raise ValueError(f"line {lineno}: empty required field {name}")
        if level not in LEVELS:
            raise ValueError(f"line {lineno}: unknown level {level}")
        if topic not in TOPIC_KEYS:
            raise ValueError(f"line {lineno}: unknown topic {topic}")
        if not ex2ja or not ex2zh:
            raise ValueError(f"line {lineno}: second example is required")
        readings = romaji_table.get(id_)
        if not readings or len(readings) != 2 or not all(readings):
            raise ValueError(f"line {lineno}: no romaji readings for {id_}; run gen_romaji.py first")
        entries.append({
            "id": id_,
            "w": w,
            "kana": kana,
            "romaji": romaji,
            "uk": kana,
            "us": romaji,
            "senses": [{"pos": pos, "zh": zh, "en": ja}],
            "ex": [
                {"en": ex1ja, "zh": ex1zh, "romaji": readings[0]},
                {"en": ex2ja, "zh": ex2zh, "romaji": readings[1]},
            ],
            "col": split_list(col),
            "fam": split_list(fam),
            "syn": split_list(syn),
            "ant": split_list(ant),
            "tip": tip,
            "cefr": level,
            "topic": topic,
            "note": "",
            "m": MEDIA_ALL,
        })

    topic_of = {t[0]: i for i, t in enumerate(TOPICS)}
    level_of = {lv: i for i, lv in enumerate(LEVELS)}
    words = [
        [e["id"], e["w"], f"{e['senses'][0]['pos']} {e['senses'][0]['zh']}", e["kana"], level_of[e["cefr"]], topic_of[e["topic"]], MEDIA_ALL]
        for e in entries
    ]
    index = {
        "id": "word-atlas-ja-open",
        "version": 1,
        "name": "Daijoubu Open",
        "language": "ja",
        "scale": "JLPT",
        "license": "CC BY 4.0",
        "count": len(entries),
        "examples": sum(len(e["ex"]) for e in entries),
        "illustrated": len(entries),
        "voiced": len(entries),
        "chunk": CHUNK,
        "topics": TOPICS,
        "cefr": LEVELS,
        "fields": ["id", "word", "meaning", "kana", "level", "topic", "media"],
        "words": words,
    }

    ATLAS.mkdir(parents=True, exist_ok=True)
    chunks = ATLAS / "entries"
    if chunks.exists():
        shutil.rmtree(chunks)
    chunks.mkdir(parents=True)
    for n, start in enumerate(range(0, len(entries), CHUNK)):
        (chunks / f"{n}.json").write_text(
            json.dumps(entries[start:start + CHUNK], ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
    (ATLAS / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    (DATA / "word-atlas-ja.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with (DATA / "word-atlas-ja.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "w", "kana", "romaji", "pos", "zh", "ja", "level", "topic", "ex1_ja", "ex1_zh", "ex2_ja", "ex2_zh", "col", "fam", "syn", "ant", "tip"])
        for e in entries:
            writer.writerow([
                e["id"], e["w"], e["kana"], e["romaji"], e["senses"][0]["pos"],
                e["senses"][0]["zh"], e["senses"][0]["en"], e["cefr"], e["topic"],
                e["ex"][0]["en"], e["ex"][0]["zh"], e["ex"][1]["en"], e["ex"][1]["zh"],
                "; ".join(e["col"]), "; ".join(e["fam"]), "; ".join(e["syn"]), "; ".join(e["ant"]), e["tip"],
            ])

    by_level = {lv: sum(1 for e in entries if e["cefr"] == lv) for lv in LEVELS}
    by_topic = {t[0]: sum(1 for e in entries if e["topic"] == t[0]) for t in TOPICS}
    print(json.dumps({
        "words": len(entries),
        "examples": index["examples"],
        "chunks": len(list(chunks.glob("*.json"))),
        "levels": by_level,
        "emptyTopics": [k for k, v in by_topic.items() if v == 0],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(build())
