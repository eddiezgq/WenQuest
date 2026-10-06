# 网页互动课件：写法（第 24 轮）

每讲一个 `chNN.yaml`，`python3 course/tools/build_slides.py chNN --out <目录> --preview all` 生成单个网页课件和逐页预览截图。
标准见 `docs/方案/网页互动课件标准.md`；范例是 `ch01.yaml`（Eddie 认可的样品），新写的讲照它的密度、语气和节奏。

## 文件头

```yaml
lesson: 2                 # 讲号
code: [ch02]              # 课程包程序 course/calc/ch02.py；文字里写 {{ch02.键:格式}}，由程序算出（程序末尾在设了 WQ_BOOK_OUT 时 out(...) 交出这些键）
clips:                    # “活”的片段：在页里运行的动画、实验、三维样机（src/zh/labs/<page>.html）
  hero: {page: proto-lockstitch, selector: "#stage", steps: [{at: 0, press: "#shell [data-k=clear]"}]}
  anim: {page: lockstitch, selector: "#mech", steps: [{at: 0, set: {speed: 15}}]}
slides: [...]
```

clip 的字段：`page` 实验页名；`selector` 只显示页面里的这一块（不写就显示整页）；`steps` 打开后自动做的操作：
`{at: 秒, press: "CSS 选择器" 或列表, set: {元素id: 值}, js: "页面里执行的代码"}`；`vw/vh` 页面在框里的虚拟尺寸（默认 1600×900）。
带 `#stage` 的三维页自动铺满（cover）。先用浏览器看一眼实验页，找到合适的 selector（画布、三维舞台等）。

## 版式（`layout`），每页一种

| layout | 字段 | 用途 |
|---|---|---|
| `cover` | `video`（clip 名）、`kicker` `title` `sub`（中英对） | 封面：活的三维模型或动画作背景 |
| `question` | `tag` `title` `facts`（3 条） | 车间问题 |
| `section` | `num: "01"` `title` | 分节页 |
| `split` | `title` `points`（≤3） `visual` | 左要点、右图（visual 见下） |
| `points` | `title` `points`（≤3） 可选 `tag` `foot` | 只有要点 |
| `figure` | `title` `visual` 可选 `caption` `h` | 一张大图 |
| `duo` | `title` `left` `right`（各含 `video`/`fig`/`svg` 之一 + `label` `note`） | 两个对比 |
| `lab` | `title` `shot: {page, set: [{press: …}], vw, vh}` `tasks`（≤3） | 虚拟实验整页嵌入、可全屏 |
| `timeline` | `title` `events: [{year, who, what}]`（≤6） | 时间轴 |
| `stages` | `title` `stages: [{name, from, to, note}]` `foot` | 阶段条 |
| `bignum` | `title` `nums: [{n, n_en, label}]`（≤3） `foot` | 大数字 |
| `formula` | `title` `formula`（`F = m\,a \;\propto\; n^{2}` 这类简单式） `bars: [{n, F, label}]` `foot` | 公式 + 柱状对比 |
| `tiles` | `title` `tiles: [{k, name, use, hot}]`（6 个） | 六宫格 |
| `tiles4` | `title` `tiles: [{draw, name}]` | 四种线迹外观（draw: lock/chain/overedge/cover） |
| `chain` | `title` `steps`（≤9 对） `hot`（下标列表） `mark` `foot` | 流程链 |
| `answer` | `tag` `title` `rows: [[左, 右]]` `side: {big, text}` `foot` | 回到车间问题的解答 |
| `roadmap` | `title` `parts`（8 对） | 路线 |
| `summary` | `title` `points`（3） `after` | 小结与课后 |

`visual`：`{video: clip名}`（活的）、`{fig: fig_xray}`（教材插图 img/fig_xray.webp，只用图里字够大的）、`{svg: "<svg viewBox=…>…</svg>"}`（为本页新画的图）、`{html: needle_idea}`（程序里已有的几张）。

每个中英字段都写成 `["中文", "English"]`；每页可写 `notes: ["中文讲稿", "English script"]`（讲者窗口里显示，录课时照着讲，口语化，60–150 字）。
含冒号、引号的讲稿用双引号括起来。

## 规矩

1. 每页最多 3 条，每条中文不超过约 22 个字（一行半以内），英文一行；放不下就分页，不缩字号。
2. 一讲 22–30 页：封面 → 车间问题 → 3–5 节（每节：分节页 + 概念/机构 + 活页面 + 建模算例）→ 机器人联系 → 生活例子 → 解答 → 小结。每讲至少 3 处活页面（本讲的动画、实验、三维模型）。
3. 内容取自课程包 `course/lessons/chNN.json`（slides、problem、robot、life、summary、labs、assignment）和教材 `src/zh/chNN.html`；不编造事实和数字；数字由程序算出。
4. 新画的 SVG：深色底上用浅色线（#f3f6fa）、强调色 #f2b705 / #2ec4b6 / #ff7a45 / #4c8dff；字 ≥ 22 像素（viewBox 宽 900 时按 900 计），中文字体不用写（继承）。
5. 实验段只说怎样操作、观察什么，不报任务答案。
6. **所有动画完整、不断循环**：活页面里的动画放完一遍（包括“拉线头”这类会停下来的演示）要自动从头再来。会停的页面在 clip 里写 `loop: 秒`（每隔这么久重做一遍 steps），steps 里把模式按钮、播放按钮重新点上；循环周期要长于一遍完整演示。整页嵌入的实验页（`lab`）由学生操作，不自动循环。
7. 自检：`--preview all` 之后逐页看截图：没有溢出（程序会打印 `! page N overflows`）、没有重叠、活页面显示的是想要的那一块。
