# 内容生成流程 / Content pipeline

日语版的流水线全部在 `scripts/atlas/`，不需要 API 密钥，也不需要联网（例句罗马字转写需要本地 Python 包 `pykakasi`）。

| 步骤 | 脚本 | 产物 |
| --- | --- | --- |
| 1. 词表 | 人工维护 `data/ja-lexicon.txt` | 18 列词表真源 |
| 2. 罗马字 | `gen_romaji.py`（pykakasi） | `data/ja-romaji.json` |
| 3. 编译 | `build_ja_atlas.py` | `public/atlas/index.json`、`entries/*.json`、`data/word-atlas-ja.json` / `.csv` |
| 4. 插画 | `gen_ja_media.py --images-only` | `public/atlas/img/*.webp`、`thumb/*.webp` |
| 5. 朗读 | `gen_ja_media.py --audio-only` | `public/atlas/audio/{uk,us,ex,ex2}/*.mp3` |
| 6. 配音 | macOS `say` + `ffmpeg` | `public/sfx/splash-voice.mp3`、`voice-galaxy-*.mp3` |
| 7. 校验 | `npm run check:atlas` | 结构、顺序、罗马字、媒体文件存在性 |

```bash
python3 -m pip install --user pykakasi
npm run build:romaji
npm run build:atlas
npm run gen:media            # 或分别加 -- --images-only / -- --audio-only
npm run check:atlas
```

## 插画

`gen_ja_media.py` 用 Pillow 按词条 id 的哈希确定性绘制：以该话题的二次元插画（`public/brand/topic-*.webp`）为底图，叠半透明圆角信息板，板内依次写日语词头、假名、罗马字与话题级别，四角点缀花瓣。输出 512px WebP 与 160px 缩略图。脚本幂等，补词后只需重跑一次。

## 朗读

macOS 上只有 `Kyoko` 能稳定合成日语文本，其余标注 `ja_JP` 的 novelty 声库会输出空白音频。因此两条声线用同一声库的不同语速实现：`uk` / `ex` 为 `-r 165` 标准，`us` / `ex2` 为 `-r 120` 慢速。`say` 先输出 AIFF，再由 `ffmpeg` 转 24 kHz 单声道 64 kbps MP3。其他平台可换成任意日语 TTS，只要保持文件名约定。

## 质量边界

词表、释义、例句与中文翻译按统一规范整理，但未逐条人工审校；罗马字由 pykakasi 自动转写，个别复合词可能按分词切分（如 `kangae ru`），打字练习按显示串原样输入即可。自动校验只保证结构与引用正确，不保证语言学上的绝对准确。

`scripts/atlas/` 中其余脚本（`gen_text.py`、`gen_images.py`、`gen_word_audio.py` 等）来自上游英语版，保留作参考，不参与日语版构建。
