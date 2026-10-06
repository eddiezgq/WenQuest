# 公开课视频工具（第 22 轮）

讲稿 → 配音 → 逐镜头画面 → 合成（烧录字幕、水印、响度 −16 LUFS）→ 封面与上传资料。设计见《实施细则 · 第 22 轮》。

| 文件 | 作用 |
|---|---|
| `script.py` | 读讲稿、运行教材程序填数字、拆句、检查结构 |
| `voice.py` | 配音：`estimate`（无声，按字数估时长）、`kokoro`（开源占位声音）、`clone`（Eddie 本人声音，读 clone.py 的结果） |
| `clone.py` | 在租用的 GPU 上用 CosyVoice 克隆 Eddie 的声音：`audition` 试听，`lectures` 合成讲稿全部句子 |
| `slides.py` | Manim 画面：片头、幻灯、程序、作业、结尾、封面 |
| `labrec.py` | 虚拟实验录屏（无头浏览器 + 虚拟时钟，逐帧） |
| `make.py` | 总控：渲染各镜头、合成成片 |

## 讲稿格式（`docs/课程视频/<课>/<节>/讲稿.yaml`）

```yaml
book: linalg            # 教材代号
section: "14.2"
code: [ex14_2]          # 要运行的教材程序，输出可用 {{ex14_2.kmin:.0f}} 引用
title: [中文题目, English title]
chapter: [第 14 章 …, Chapter 14 …]
next: [下一讲, Next lecture]
cover_formula: 'A = Q\Lambda Q^{\mathsf T}'   # 封面上的公式
shots:
  - id: problem
    kind: slide          # title / slide / anim / code / lab / clip / homework / outro
    part: [实际问题, The problem]      # 章节时间点的名字
    head: [标题, Title]
    items:               # 幻灯逐项出现：text（可夹 $公式$）、tex（整行公式）、img（教材图名，中英两版自动选）
      - img: fig14_2_1
      - text: [中文, English]
      - tex: 'A = Q\Lambda Q^{\mathsf T}'
    say:
      zh: ["一句一行。", ">行首 “>” = 说这句之前出现下一项。", "[字幕显示|配音读法]"]
      en: ["One sentence per line.", ">Same number of “>” as Chinese."]
```

其他镜头：`anim`（`src:` 教材动画名；“>” 对应动画里每个 caption 之后的下一段）、`code`（`src:` 程序名、`from:` 从哪一行起、`result:` 运行结果几行）、
`lab`（`lab: "14-2"`、`steps:` 每个 “>” 一步：`set`、`sweep`+`dur`、`press`、`demo`）、`clip`（`src:` 录屏素材，相对 `docs/课程视频/素材/`）、
`homework`（`items:` 习题编号，题目从教材原文取）、`outro`（`points:` 三条小结，每条一个 “>”）。

## 本地试做

```bash
export WQ_MANIM=manim                         # 或 manim 的完整路径
python3 textbook/tools/build.py linalg --labs # 需要教材的图和实验页
python3 tools/video/make.py docs/课程视频/线性代数/14-2 --lang zh --voice estimate --out /tmp/v --quality l
python3 tools/video/make.py docs/课程视频/线性代数/14-2 --only lab --out /tmp/v   # 只渲染某几个镜头
```

正式制作在 GitHub Actions：`Lecture videos 公开课视频`（`.github/workflows/video.yml`），结果在运行页面的 Artifacts 里。
