# 课程包每讲文件的格式（lessons/chNN.json）

《缝纫机设计与制造》课程（问渠机器人学院，一门课 31 讲，一章一讲）。每讲一个 JSON 文件，UTF-8，缩进 1。**所有给学生看的文字都是 `[中文, English]` 一对**（下文记作 PAIR），两种语言意思一致、术语按 `../GLOSSARY.md`。文字是纯文本（可以用 Unicode 符号如 ω、°、≤、×10⁻⁴），不要 HTML；公式写在专门的 `formula` 字段里（LaTeX，不加 `\[ \]`）。

```json
{
  "no": 13,
  "title": PAIR,                                  // 与教材章名一致（book.py）
  "hours": 4,                                     // 建议学时（2–6）
  "goals": [PAIR, ...],                           // 3–5 条学习目标，可检验（“能算出…”“能解释…”）
  "problem": {                                    // 车间实际问题（本讲导入）：一个具体、带数字的问题，学完本讲能解决
    "title": PAIR, "text": PAIR, "question": PAIR,
    "answer": PAIR                                // 学完本讲后的解答（简要，带数字，与教材一致）
  },
  "robot": {"title": PAIR, "text": PAIR},         // 机器人联系：本讲原理在机器人上的对应（如伺服停针 ↔ 机械臂关节定位），3–5 句，具体
  "life": {"title": PAIR, "text": PAIR},          // 生活例子：1–3 句
  "slides": [                                     // PPT 正文页，10–16 页，顺序跟教材本章各节走
    {"title": PAIR,
     "points": [PAIR, ...],                       // 2–5 条要点，每条一两行
     "formula": "LaTeX 或空字符串",
     "figure": "教材插图文件名或空字符串",           // 只能用本章正文里出现的图，写 img/ 后面的文件名，如 "fig_13_stop.png"
     "narration": PAIR}                           // 这一页的讲稿（中文 120–250 字；英文对应），口语化，讲清这页
  ],
  "summary": [PAIR, ...],                         // 本讲小结 4–6 条
  "labs": [                                       // 本讲自己的虚拟实验（按下面“实验分配”），每个一份指导书
    {"id": "servo", "no": "13-1", "title": PAIR,
     "goal": [PAIR, ...],                         // 2–4 条
     "theory": [PAIR, ...],                       // 原理 2–5 条（可含公式的文字表述）
     "steps": [PAIR, ...],                        // 操作步骤 5–10 条，按实验页面真实的控件和任务写（先打开实验页看清楚）
     "record": {"caption": PAIR, "headers": [PAIR, ...], "rows": 5},   // 数据记录表
     "questions": [PAIR, ...]}                    // 思考题 2–4 条
  ],
  "assignment": {                                 // 作业 1 份
    "title": PAIR,
    "tasks": [PAIR, ...],                         // 2–4 题，至少一题是计算或设计题（给足数据），可以用教材习题改编
    "deliverable": PAIR,                          // 交什么（计算过程、截图、报告页数等）
    "rubric": [PAIR, ...]                         // 评分要点 3–5 条（带分值，如“计算正确 40 分”）
  },
  "quiz": [ QUESTION, ... ],                      // 本讲测验 8–10 题，自动评分；覆盖全讲，难度由浅到深
  "exam": [ QUESTION, ... ],                      // 给期中/期末题库的 5 题（与 quiz 不重复）
  "plan": {                                       // 教案（给老师）
    "key": PAIR, "difficult": PAIR,
    "process": [{"phase": PAIR, "minutes": 15, "content": PAIR}],   // 合计 = hours × 45 分钟
    "homework": PAIR
  }
}
```

QUESTION（测验与考试题）：

```json
{"type": "single",      "text": PAIR, "answers": [{"text": PAIR, "correct": true}, {"text": PAIR, "correct": false}, ...], "feedback": PAIR}
{"type": "multiple",    "text": PAIR, "answers": [... 至少两个 correct:true ...], "feedback": PAIR}
{"type": "truefalse",   "text": PAIR, "correct": true, "feedback": PAIR}
{"type": "numerical",   "text": PAIR, "answer": 12.5, "tolerance": 0.5, "unit": "ms", "feedback": PAIR}
```

- single 4 个选项、恰好 1 个对；multiple 4–5 个选项、2–3 个对；每讲 quiz 里 numerical 至少 2 题，题目给足数据，答案由你用 Python 算出并核对。
- feedback 写清为什么（一两句）。
- 不出“以上都对”“以下哪个不是”这类题；干扰项要像样（常见错误）。

## 硬规则

1. **依据教材**：内容、数字、公式、术语都与本章正文 `../src/zh/chNN.html`、`../src/en/chNN.html` 一致；有疑问以教材为准，不要引入教材里没有、你又无法确认的事实或数据。
2. **课程标准**：本讲导入按“实际问题（车间）→ 概念 → 动画/虚拟实验 → 建模求解”，`problem.answer` 要用本讲的模型算出来。机器人联系要具体，不要空话。
3. 数字一律由计算得到（用 Python 算，脚本可以放 `course/calc/chNN.py`），不要估算。
4. 写完用 `python3 course/tools/check.py chNN` 自检（格式、成对、图片存在、题目合法），直到 0 个错误。
