# 问渠教材源文件

本目录放问渠自编教材的源文件。目前有：

- 《机器人学》`robotics/`：提纲 `docs/教材/机器人学/00_提纲.md`，开发计划见《实施细则 · 第 7、8 轮》；
- 《大学物理》`physics/`：提纲 `docs/教材/大学物理/00_提纲.md`，开发计划见《实施细则 · 第 9 轮》；
- 《线性代数》`linalg/`：见《实施细则 · 第 10 轮》。

各书用同一套工具和写法。新增一本书：写提纲，在 `textbook/<书>/meta.yaml` 里写提纲路径和书名（第 10 轮的做法），运行 `outline.py <书>` 生成 `book.yaml`。CI 会自动构建 `textbook/` 下每一本有 `book.yaml` 的书。

## 目录

```
textbook/
  robotics/
    book.yaml             目录（由提纲生成，不要手改）
    conventions/          符号约定.md、术语表.csv、参考书目.md
    chNN/NN-M.md          正文，一节一个文件
    chNN/code/*.py        算例程序：书中的数字由它们算出
  tools/                  构建与检查工具
  build/                  构建结果（不进仓库）
```

## 写一节

1. 文件开头写节号和节名：

   ```
   ---
   id: "4.1"
   title: 平面转动与旋转矩阵
   ---
   ```

   节号必须在提纲里。节里的小节写成 `### 4.1.1 问题的提出`。

2. **公式**用 LaTeX：行内 `$...$`，独立公式 `$$...$$`。要编号的公式写 `\tag{4.1.3}`，按节从 1 起连续编号。

3. **计算得到的数字一律由程序给出**。程序写在 `code/ex4_1_1.py`，最后调用：

   ```python
   from bookout import out
   out(x_p=0.12321)
   ```

   正文里写成 `{{ex4_1_1.x_p}}`，默认 5 位有效数字；要别的格式就写 `{{ex4_1_1.phi_deg:.2f}}`。

   4 位及以上有效数字的小数如果是手写的，检查会拦下。题目给定的数据（如 0.2 m）可以手写。

4. **程序、动画、实验、图**：

   ```
   ::: 程序 4.1.1
   src: code/ex4_1_1.py
   说明: 两种算法计算算例 4.1.1
   :::
   ```

   虚拟实验写成 `::: 实验 4.3` / `src: lab4_3`，程序放在 `lab/lab4_3.js`。每个实验还要有一份说明文件 `lab/lab4_3.yaml`，用来生成《实验指导书》和《实验报告模板》（Word）。说明文件写：原理（每项是 `[中文, English]`，公式写成 `式: ...`）、步骤、数据表（标题、表头、行，每行格数与表头一致）、注意，可选“思考题”。实验目的、场景、可调参数、任务和第一道思考题直接取自实验程序，不要重复写。没有说明文件或格式不对，构建会失败。

   三维实验写 `view: "3d"` 和 `models: ["B-ARM-UR5E"]`，模型必须先复制到本书的 `models/` 文件夹：`python3 tools/models.py robotics <零件库版本> <模型编号…>`。构建时把用到的模型嵌入本章实验页。

5. **编号项**：写成 `**定义 4.1.1（名称）**`、`**定理 4.1.1**`、`**算例 4.1.1**`，物理书还有 `**定律 6.2.1（名称）**`（英文 `**Law 6.2.1**`），各自从 1 起连续编号。正文中引用时写“式 (4.1.3)”“定理 4.1.1”“4.8 节”“第 5 章”，检查会核对目标是否存在。

6. **术语**：第一次出现时加粗 `**旋转矩阵**`，必须已在 `conventions/术语表.csv` 里；新术语先登记，再使用。同一个中文术语在两本书里的英文名必须相同（至少有一个英文名相同，括号里的说明不算），否则构建失败。加粗只用于术语，不用于强调。

   书的物理常数（物理书）在 `conventions/constants.py`，程序里 `from constants import g, c, h`。

7. **符号**：按 `conventions/符号约定.md`。

## 构建与检查

第一次使用先安装工具：

```
cd textbook/tools && npm ci
pip install markdown-it-py pyyaml numpy
```

然后：

```
python3 textbook/tools/build.py robotics          # 检查并生成网页版
python3 textbook/tools/build.py robotics --pdf    # 同时生成每章 PDF
python3 textbook/tools/build.py robotics --only 4.1
```

结果在 `textbook/build/robotics/`：
- `web/`：每节一个 HTML 片段和 `index.json`，供平台阅读页使用；
- `chNN.html`、`chNN.pdf`：整章的网页和 PDF；
- `report.txt`：检查报告。

**任何错误都会让构建失败，推送后 CI 也会跑同样的检查。**

**提纲改了以后**，运行 `python3 textbook/tools/outline.py robotics` 重新生成 `book.yaml`。

## 英文版（第 8 轮）

- 每节的英文版写在中文旁边：`NN-M.en.md`，开头 `id` 与中文相同、`title` 为英文。一章的英文章名、各章状态写在 `robotics/progress.yaml`。
- 结构与中文一一对应（构建检查）：公式编号、`::: Figure / Program / Animation / Lab / Table`（键名 `caption:`、`figure:`、`src:`）、`**Definition / Theorem / Lemma / Corollary / Example x.y.z**`、习题编号、小节编号、占位符。引用写 Eq. (x.y.z)、Figure、Example、Section x.y、Chapter n。
- 加粗术语必须是术语表 English 列里的名称；中文加粗的术语，英文也要加粗对应的名称。英文正文里不能留中文。
- 示意图和程序交给正文的文字用 `bookout.T("中文", "English")`；构建时每个程序再以英文运行一次（`WQ_LANG=en`），图存到 `figs/en/`，数字必须与中文运行相同。
- 正文列出的程序要有英文注释的副本 `code/en/同名.py`，只许改注释和文档字符串。
- 实验说明 yaml 的数据表有中文时，加 `表头英文`、`行英文`，用来生成英文的实验指导书和报告模板。
- 翻译时可先用 `python3 tools/check_en.py robotics/chNN/NN-M.en.md` 快速检查一节。
