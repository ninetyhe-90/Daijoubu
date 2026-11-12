import { ArrowUpRight, Database, Github, Heart } from "lucide-react";
import { useAtlas } from "../atlas/context";
import { REPO_URL } from "../config";

const BASE = import.meta.env.BASE_URL;

export function About() {
  const atlas = useAtlas();
  return (
    <div className="page about">
      <header className="about-hero">
        <img src={`${BASE}brand/og.webp`} alt="" />
        <div>
          <p className="eyebrow">关于大米要扛几楼 日本語版</p>
          <h1 className="display">一词一画，点亮日语。</h1>
          <p className="lede">
            大米要扛几楼 日本語版把 JLPT N5 到 N1 的常用词整理成 {atlas.count.toLocaleString()} 个词条。每个词一幅原创插画，一句日常例句，一句能力考语境例句，配假名、罗马字、双声线日语朗读、常用搭配和易混提示。学会一个，就在你的星图上点亮一颗星。
          </p>
          <p className="lede">它免费、开源、无需注册。代码用 MIT，词库与插画、录音用 CC BY 4.0，谁都可以拿去用。</p>
          <div className="about-actions">
            <a className="btn btn-primary" href={REPO_URL} target="_blank" rel="noreferrer">
              <Github size={18} /> 查看上游项目
            </a>
            <a className="btn btn-ghost" href={`${BASE}atlas/index.json`} target="_blank" rel="noreferrer">
              <Database size={18} /> 查看词库数据
            </a>
          </div>
        </div>
      </header>

      <div className="about-grid">
        <section className="panel">
          <h3 className="eyebrow">为什么记得住</h3>
          <ul className="feature-list">
            <li>
              <b>先看见。</b>每个词都有一幅画，画的就是这个词的核心意思。
            </li>
            <li>
              <b>再想起。</b>选义、看图补句、听音辨词、罗马字拼写，从认得走到会写。
            </li>
            <li>
              <b>刚好在快忘时重逢。</b>FSRS 是新版 Anki 用的开源记忆算法，只在你快要遗忘时安排复习。
            </li>
            <li>
              <b>分数诚实。</b>只算第一次作答。答错的词会换个题型再见一面，但不会抬高正确率。
            </li>
            <li>
              <b>进度只属于你。</b>没有账号，没有服务器，数据存在你的浏览器里，随时能导出。
            </li>
          </ul>
        </section>

        <section className="panel">
          <h3 className="eyebrow">快捷键</h3>
          <dl className="keys">
            <div>
              <dt>
                <kbd>⌘</kbd>
                <kbd>K</kbd> 或 <kbd>/</kbd>
              </dt>
              <dd>搜索任何词</dd>
            </div>
            <div>
              <dt>
                <kbd>1</kbd>–<kbd>4</kbd>
              </dt>
              <dd>选择答案</dd>
            </div>
            <div>
              <dt>
                <kbd>Enter</kbd>
              </dt>
              <dd>确认 / 继续</dd>
            </div>
            <div>
              <dt>
                <kbd>←</kbd> <kbd>→</kbd>
              </dt>
              <dd>词卡里切换上一个、下一个</dd>
            </div>
            <div>
              <dt>
                <kbd>Esc</kbd>
              </dt>
              <dd>关闭弹窗</dd>
            </div>
          </dl>
        </section>

        <section className="panel">
          <h3 className="eyebrow">内容从哪里来</h3>
          <p className="muted">
            词条、释义、例句和中文翻译按统一的词典规范人工整理；插画用和纸纹样与日语字样按词条确定性绘制；单词与例句朗读由 macOS 日语语音（Kyoko、Sandy）合成，分别对应标准与慢速两条声线。例句的罗马字由 pykakasi 转写，供打字练习使用。所有内容都经过结构与一致性的自动校验，但没有逐条人工审校。
          </p>
          <p className="muted">这不是官方 JLPT 词表，也不承诺提分。它只想把背日语单词这件事，做得好看一点、扎实一点。</p>
        </section>

        <section className="panel">
          <h3 className="eyebrow">给开发者</h3>
          <p className="muted">
            <code>data/ja-lexicon.txt</code> 是词表真源，<code>data/word-atlas-ja.json</code> 和 <code>.csv</code> 是完整词库；<code>public/atlas</code> 里是网页用的分块数据、插画和音频。拿去做 Anki 牌组、背词小程序、浏览器插件，或者 AI 应用的评测集，署名即可。
          </p>
          <a className="link" href={`${REPO_URL}#readme`} target="_blank" rel="noreferrer">
            阅读上游文档 <ArrowUpRight size={14} />
          </a>
        </section>
      </div>
      <p className="colophon">
        <Heart size={14} /> 做给每一个在背日语单词的人。
      </p>
    </div>
  );
}
