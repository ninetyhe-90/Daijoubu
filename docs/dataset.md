# 词库格式 / Dataset format

## `data/ja-lexicon.txt`

词表真源。管道 `|` 分隔，18 列，一行一个词条，空字段允许连续 `||`：

`id|w|kana|romaji|pos|zh|ja|level|topic|ex1ja|ex1zh|ex2ja|ex2zh|col|fam|syn|ant|tip`

| 列 | 说明 |
| --- | --- |
| `id` | 罗马字 slug，只含 `[a-z0-9-]`，同时是媒体文件名 |
| `w` | 日语词头（汉字与假名混写） |
| `kana` / `romaji` | 假名读音 / 罗马字读音 |
| `pos` | 日语词性，如 `名詞`、`動詞`、`形容詞` |
| `zh` / `ja` | 中文释义 / 简明日语释义 |
| `level` | JLPT 级别：`N5` `N4` `N3` `N2` `N1` |
| `topic` | 19 个话题键之一 |
| `ex1*` / `ex2*` | 日常短句与能力考语境长句，各含日文与中文 |
| `col` | 常用搭配，多个用 `;` 分隔，每条为 `日本語｜中文` |
| `fam` / `syn` / `ant` | 词族 / 近义 / 反义，多个用 `;` 分隔 |
| `tip` | 一条中文用法或辨析提示 |

## `data/word-atlas-ja.json`

一个数组，按词表顺序排列。为兼容上游数据结构，部分字段名沿用英文语义：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` / `w` | string | URL 安全标识 / 日语词头 |
| `kana` / `romaji` | string | 假名 / 罗马字读音（日语版新增） |
| `uk` / `us` | string | 兼容字段，分别存 `kana` / `romaji`；对应的音频位也沿用 `uk`、`us` |
| `senses` | `{pos, zh, en}[]` | 义项：日语词性、中文释义、简明日语释义（`en` 槽位存日语） |
| `ex` | `{en, zh, romaji}[]` | 两条例句：日文、中文、罗马字转写 |
| `col` / `fam` / `syn` / `ant` | string[] | 搭配、词族、近义、反义 |
| `tip` / `note` | string | 用法提示 / 可选提醒 |
| `cefr` | string | 兼容字段，值为 JLPT 级别 `N5`…`N1` |
| `topic` | string | 19 个话题之一：education, work, technology, science, environment, health, society, government, economy, media, arts, travel, city, nature, daily, emotion, thinking, sport, history |
| `m` | number | 媒体位标记，当前所有词条为 `31`（全部具备） |

`data/word-atlas-ja.csv` 是同样内容的表格版，UTF-8 编码。

## 网页数据 `public/atlas/`

- `index.json`：紧凑索引。`cefr` 数组为 `["N5","N4","N3","N2","N1"]`；`words` 每行为 `[id, word, zh, kana, levelIndex, topicIndex, media]`。
- `entries/<n>.json`：完整词条，每块 100 条，第 `n` 块对应索引第 `n*100` 到 `n*100+99` 行。
- `img/<id>.webp`（512px）、`thumb/<id>.webp`（160px）。
- `audio/uk/<id>.mp3`：词头标准朗读；`audio/us/<id>.mp3`：假名慢速朗读。
- `audio/ex/<id>.mp3`：第一条例句朗读；`audio/ex2/<id>.mp3`：第二条例句慢速朗读。

`media` 位标记：`1` 插画、`2` 词头、`4` 假名慢速、`8` 例句一、`16` 例句二。媒体覆盖情况一律以 `index.json` 的位标记为准。

## 授权

CC BY 4.0，署名 “Daijoubu contributors”。见 [CONTENT_LICENSE.md](../CONTENT_LICENSE.md)。
