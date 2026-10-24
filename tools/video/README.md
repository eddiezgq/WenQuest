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

## 网页版教材（第 23 轮：《缝纫机设计与制造》）

- 讲稿写 `book: sewing`、`section: "2"`（讲号 = 课程包一讲 = 教材一章），放 `docs/课程视频/缝纫机/NN/`。
- `code: [ch02]` 运行课程包程序 `course/calc/ch02.py`（程序末尾在设了 `WQ_BOOK_OUT` 时用 `bookout.out` 交出视频要引用的数）。
- 插图 `img: fig_xray` 取 `img/fig_xray.webp`（英文版优先 `img/en/`）。
- `homework` 的 `items: [1, 2, 3, 4]` 是课程包作业第几题；`foot` 可自定一行说明。
- `lab` 镜头直接打开 `src/<语言>/labs/<lab>.html`（动画、虚拟实验、三维样机都这样录）；`book: true` 改为录网页版教材本章页面（工具先构建一次）。
  步骤按元素 id：`set: {delta: 10}`（滑块、下拉框、勾选框）、`sweep`、`press: "#play"`（可列表）、`js: "…"`、`click: [x, y]`、`drag`；同一步里的几个动作一起做。
- 网页一律按 15 帧/秒录、合成时补成 30 帧；页面带 `__api.manual/step` 的三维页不用虚拟时钟，逐帧推进（软件渲染每帧约 1 秒）。
  本地没有外网时设 `WQ_THREE=…/three.min.js`（r128）。


## 课件即画面（第 25 轮起的标准，2026-10-08）

讲稿只写开场、课后部分和结尾，正片自动由网页互动课件生成：

```yaml
book: sewing
section: "3"
deck: ch03                 # course/slides/ch03.yaml：每页一个镜头，配音 = 该页 notes，按句子逐条出现要点
skip: [6, 21, 23]          # 控制长度时跳过的页
intro: {zh: [...], en: [...]}      # 封面上说的话
after:                     # 课程讲完、小结之前：实验录屏（kind: lab，格式同上）或追加的课件页
  - {id: homework, part: [作业, Assignment], slide: {layout: points, ...}, say: {zh: [...], en: [...]}}
outro: {zh: [...], en: [...]}      # 小结页讲稿之后再说的话（注册引导、下一讲）
```

- 课件里的整页实验（`lab` 版式）和小结页不按原位置出现：实验放到课后部分用实验录屏，小结放在最后。
- 中文版录双语课件，英文版录 `make_deck(..., lang="en")` 生成的英文版课件（只显示英文、嵌英文实验页）。
- 三维片段（`proto-*`、`model-*`）先在三维页上逐帧录好，课件录屏时按帧换图（`__wqFrame`），其余动画按虚拟时钟实时运行。

## 独立视频：外部网页课件（第 38 轮）

不属于哪本教材的视频（如《WenQuest Ops 介绍》），画面直接录一份做好的网页课件（每页一个 `section.pg`，带 `window.__deck`：
`go(页下标, 步)`、`next()`、`fragments(页下标)`、`state()`）。讲稿放 `docs/课程视频/<名字>/讲稿.yaml`：

```yaml
standalone: true
langs: [en]                 # 只配这几种语言（clone.py 也只合成这些）
subs: en+zh                 # 英文配音，字幕英文在上、中文在下；画面缩到 85 % 放上面，下面是字幕带
title: [中文名, English title]
deck_html: 课件/index.html  # 相对讲稿目录
contact: someone@example.com   # 写进上传资料（可不写）
pace: {speed: 1.3, head: 0.45, pause: 0.12, tail: 0.45, hold: 0.25, xfade: 0.4}   # 可选：语速倍数，镜头头尾、句间、每步后停顿与转场（秒）
shots:
  - id: s01
    kind: page
    page: 28                # 课件第几页（从 1 起）
    part: [中枢, The hub]   # 章节时间点
    steps:                  # 与 “>” 一一对应
      - {show: 1}                                  # 要点出现到这一页的 100 %（0.5 = 一半）
      - {click: "tr.click", text: "SO-1042"}       # 点这一页里含这段字的元素（金色框提示点了哪里；i: 第几个）
      - {type: ["#dohS", 0, "0"]}                  # 在输入框里填值
      - {js: "__C(28, '#nx'); __C(28, '#nx')"}     # 直接执行（__C 点击、__Y 填值、__N 出要点）
    say:
      en: [">Back to Tuesday.", ">Click the late order and follow the chain."]
      zh: [">回到那个周二。", ">点开迟到的订单，顺着链往下看。"]     # 双语字幕时只作字幕，与英文逐句对应
```

- 课件页里的白板动画（`iframe.wbf`，`data-t0`/`data-t1` 是白板上的起止秒）随镜头时长同步画完，不出白板自己的声音。
- 先在本机检查每步操作：`python3 tools/video/make.py <讲稿目录> --lang en --voice kokoro --out /tmp/v --only s01,s15`。
- 从分支运行工作流时，运行记录和预览提交回那个分支，不进 main。
