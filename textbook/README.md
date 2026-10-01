# 问渠教材源文件

本目录放问渠自编教材的源文件。第一本是《机器人学》，提纲见 `docs/教材/机器人学/00_提纲.md`，开发计划见《实施细则 · 第 7 轮》。

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

5. **编号项**：写成 `**定义 4.1.1（名称）**`、`**定理 4.1.1**`、`**算例 4.1.1**`，各自从 1 起连续编号。正文中引用时写“式 (4.1.3)”“定理 4.1.1”“4.8 节”“第 5 章”，检查会核对目标是否存在。

6. **术语**：第一次出现时加粗 `**旋转矩阵**`，必须已在 `conventions/术语表.csv` 里；新术语先登记，再使用。

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
