#!/usr/bin/env python3
"""Generate Japanese illustrations and speech recordings for the atlas.

Illustrations: 512 px WebP plus 160 px thumbnails, deterministic per word.
Each card uses the anime-style artwork of its topic as a backdrop.
Audio: four MP3 tracks per word (headword, kana, example 1, example 2),
synthesised with the macOS Japanese voices and encoded with ffmpeg.
"""

import argparse
import hashlib
import json
import random
import subprocess
import sys
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "public" / "atlas"
BRAND = ROOT / "public" / "brand"
DATA = ROOT / "data" / "word-atlas-ja.json"
FONT_PATH = "/System/Library/Fonts/Hiragino Sans GB.ttc"

# Bright anime palette: ink colour for the lettering plus a soft accent.
TOPIC_THEMES = [
    ("#4E86C6", "#F2A0B6", "教育"), ("#C97A5B", "#F6C177", "职场"),
    ("#4B9FB0", "#9AD9C8", "科技"), ("#5A78C4", "#A7B8F5", "科学"),
    ("#4E9B74", "#A8D98A", "环境"), ("#D0708C", "#FFB3C1", "健康"),
    ("#7A6BB5", "#D7C1F0", "社会"), ("#5A6BA8", "#C0CFF2", "政法"),
    ("#C08A3E", "#F5D488", "经济"), ("#3F8FB5", "#9BD3EE", "媒体"),
    ("#C06A8A", "#F3B6C8", "艺术"), ("#3F9C93", "#A5E0D0", "旅行"),
    ("#5A7FA8", "#B7D5F0", "城市"), ("#4E9368", "#B6DE9A", "自然"),
    ("#C1774E", "#F6C9A0", "生活"), ("#C4668F", "#F4AFD0", "情感"),
    ("#5A72B8", "#B9C8F5", "思维"), ("#C08A3E", "#F5D488", "运动"),
    ("#8A6BA8", "#D8BEF0", "历史"),
]

TOPIC_KEYS = [
    "education", "work", "technology", "science", "environment", "health",
    "society", "government", "economy", "media", "arts", "travel", "city",
    "nature", "daily", "emotion", "thinking", "sport", "history",
]

# Kyoko is the only macOS voice that actually synthesises Japanese text;
# the second track is the same voice at a slower rate.
VOICE_MAIN = "Kyoko"
VOICE_ALT = "Kyoko"
RATE_NORMAL = "165"
RATE_SLOW = "120"


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def font(size):
    return ImageFont.truetype(FONT_PATH, size, index=0)


def seed_of(text):
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def make_image(entry, topic_index, dest_full, dest_thumb):
    size = 512
    base = hex_rgb(TOPIC_THEMES[topic_index][0])
    accent = hex_rgb(TOPIC_THEMES[topic_index][1])
    seed = seed_of(entry["id"])
    rnd = random.Random(seed)

    art = ImageOps.fit(
        Image.open(BRAND / f"topic-{TOPIC_KEYS[topic_index]}.webp").convert("RGB"),
        (size, size),
        Image.Resampling.LANCZOS,
    )
    img = Image.blend(art, Image.new("RGB", (size, size), (255, 250, 242)), 0.12)

    plate = (42, 54, size - 42, size - 54)
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle(plate, radius=30, fill=(255, 253, 248, 232), outline=mix(base, (255, 255, 255), 0.55) + (255,), width=4)
    ld.rounded_rectangle(
        (plate[0] + 12, plate[1] + 12, plate[2] - 12, plate[3] - 12),
        radius=22,
        outline=mix(accent, (255, 255, 255), 0.35) + (255,),
        width=2,
    )
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    d = ImageDraw.Draw(img)

    for _ in range(40):
        x, y = rnd.randrange(size), rnd.randrange(size)
        if plate[0] < x < plate[2] and plate[1] < y < plate[3]:
            continue
        r = 3 + rnd.random() * 5
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=mix(accent, (255, 255, 255), 0.45))

    word = entry["w"]
    word_size = 96 if len(word) <= 2 else 78 if len(word) <= 4 else 58 if len(word) <= 6 else 44
    f_word = font(word_size)
    box = d.textbbox((0, 0), word, font=f_word)
    d.text(
        ((size - (box[2] - box[0])) / 2 - box[0], 204 - (box[3] - box[1]) / 2 - box[1]),
        word,
        font=f_word,
        fill=mix(base, (28, 34, 46), 0.55),
    )

    f_kana = font(30)
    kana = entry["kana"]
    box = d.textbbox((0, 0), kana, font=f_kana)
    d.text(((size - (box[2] - box[0])) / 2 - box[0], 296), kana, font=f_kana, fill=mix(base, (90, 96, 110), 0.45))

    f_romaji = font(22)
    romaji = entry["romaji"]
    box = d.textbbox((0, 0), romaji, font=f_romaji)
    d.text(((size - (box[2] - box[0])) / 2 - box[0], 338), romaji.upper(), font=f_romaji, fill=mix(base, (90, 96, 110), 0.55))

    d.line([100, 378, 412, 378], fill=mix(accent, base, 0.5), width=2)
    f_tag = font(22)
    tag = f"{TOPIC_THEMES[topic_index][2]}  /  {entry['cefr']}"
    box = d.textbbox((0, 0), tag, font=f_tag)
    d.text(((size - (box[2] - box[0])) / 2 - box[0], 392), tag, font=f_tag, fill=mix(base, (60, 68, 84), 0.6))

    f_mark = font(20)
    outline = mix(base, (30, 38, 64), 0.55)
    d.text((60, 26), "大米要扛几楼", font=f_mark, fill=(255, 255, 255), stroke_width=2, stroke_fill=outline)
    d.text((size - 92, 460), f"No.{seed % 9000 + 1000}", font=f_mark, fill=(255, 255, 255), stroke_width=2, stroke_fill=outline)

    dest_full.parent.mkdir(parents=True, exist_ok=True)
    dest_thumb.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest_full, "WEBP", quality=84, method=4)
    img.resize((160, 160), Image.LANCZOS).save(dest_thumb, "WEBP", quality=76, method=4)


def make_audio(text, voice, rate, dest, tmp_dir):
    dest.parent.mkdir(parents=True, exist_ok=True)
    aiff = Path(tmp_dir) / f"ja-{uuid.uuid4().hex}.aiff"
    subprocess.run(["say", "-v", voice, "-r", rate, "-o", str(aiff), text], check=True, capture_output=True)
    subprocess.run(
        ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(aiff),
         "-codec:a", "libmp3lame", "-b:a", "64k", "-ar", "24000", "-ac", "1", str(dest)],
        check=True, capture_output=True,
    )
    aiff.unlink(missing_ok=True)


def build(entries, topics, jobs, force, images, audio, tmp_dir):
    topic_index = {t[0]: i for i, t in enumerate(topics)}
    paths = ATLAS
    tasks = []
    if images:
        for e in entries:
            full = paths / "img" / f"{e['id']}.webp"
            thumb = paths / "thumb" / f"{e['id']}.webp"
            if force or not full.exists() or not thumb.exists():
                tasks.append(("image", e, topic_index[e["topic"]], full, thumb))
    if audio:
        specs = [
            ("uk", lambda e: e["w"], VOICE_MAIN, RATE_NORMAL),
            ("us", lambda e: e["kana"], VOICE_ALT, RATE_SLOW),
            ("ex", lambda e: e["ex"][0]["en"], VOICE_MAIN, RATE_NORMAL),
            ("ex2", lambda e: e["ex"][1]["en"], VOICE_ALT, RATE_SLOW),
        ]
        for e in entries:
            for kind, get_text, voice, rate in specs:
                dest = paths / "audio" / kind / f"{e['id']}.mp3"
                if force or not dest.exists():
                    tasks.append(("audio", get_text(e), voice, rate, dest))

    def run(task):
        if task[0] == "image":
            _, _, ti, full, thumb = task
            make_image(task[1], ti, full, thumb)
        else:
            _, text, voice, rate, dest = task
            make_audio(text, voice, rate, dest, tmp_dir)
        return 1

    print(f"tasks: {len(tasks)} (workers={jobs})")
    done = 0
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = [pool.submit(run, t) for t in tasks]
        for fut in as_completed(futures):
            fut.result()
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(tasks)}", flush=True)
    print(f"completed: {done}")
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--images-only", action="store_true")
    ap.add_argument("--audio-only", action="store_true")
    args = ap.parse_args()
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    idx = json.loads((ATLAS / "index.json").read_text(encoding="utf-8"))
    images = not args.audio_only
    audio = not args.images_only
    with tempfile.TemporaryDirectory(prefix="daijoubu-aiff-") as tmp:
        build(payload, idx["topics"], args.workers, args.force, images, audio, tmp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
