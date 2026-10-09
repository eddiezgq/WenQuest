# 《数字工厂实训》网页版（第 29 轮）

副标题“智能工厂运营与决策”。一讲一章，12 章；课程大纲见 `docs/课程体系/数字工厂实训/大纲.md`，本轮细则见 `docs/实施细则/第29轮_2026-10-08_数字工厂实训课样板.md`。第 29 轮先写样板讲 3、6、10，其余各章在目录里标“编写中”，课程包里标“建设中”。

格式和《缝纫机设计与制造》网页版相同（`../sewing/README.md`），网页课件、课程包、检查用公用工具 `textbook/tools/webcourse/`，本书的差别都写在 `course/course.yaml`。

## 目录

| 位置 | 内容 |
|---|---|
| `book.py` | 篇、章的中英文标题与要点 |
| `src/zh/chNN.html`、`src/en/chNN.html` | 各章正文片段 |
| `src/zh/labs/*.html` | 动画与虚拟实验（每个自成一页，中英文字都在页内的 `TX` 字典里，按 `<html lang>` 选） |
| `src/en/labs/*.html` | 由 `tools/sync_labs.py` 从中文页生成，不手改 |
| `img/*.webp`、`img/en/*.webp` | 插图（中文、英文）；生成程序在 `figsrc/` |
| `res_zh.json`、`res_en.json` | “互动资源”页的清单 |
| `course/course.yaml` | 课程包与课件的按书配置（课名、讲数、建设中的讲、数字工厂地址、视频上传文字） |
| `course/calc/chNN.py` | 每讲的计算程序：教材、课件、题目里的数字都从这里来；模型和参数直接读数字工厂（`factory/digital/sim/`、`hub/`） |
| `course/gen/chNN.py` | 生成 `course/lessons/chNN.json`（讲义、实验指导、作业、测验、教案） |
| `course/slides/chNN.yaml` | 网页互动课件 |

## 构建与检查

```bash
python3 build.py out                                  # 网页版（含课件）
python3 course/tools/check.py all                     # 每讲课程文件检查
python3 course/tools/build_course.py /tmp/pack        # 课程包
python3 course/tools/build_slides.py ch06 --out /tmp/deck --preview all   # 课件逐页截图
```

改了实验页：先改 `src/zh/labs/`，再 `python3 tools/sync_labs.py`。改了某讲的数字或题目：改 `course/calc/chNN.py` 或 `course/gen/chNN.py`，再运行 `python3 course/gen/chNN.py`。

## 数字工厂实验

每讲的数字工厂实验写在课程文件的 `factory_labs`（如 `lab18`）。课程包里生成三个链接：打开数字工厂实验页、指导书、报告模板（`https://factory.wenquestrobotics.com/api/cae/<实验>/guide.docx`，公开）。实验的自动评分在数字工厂“实验与任务”里，报告交到本讲作业。
