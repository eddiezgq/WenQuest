# 《缝纫机设计与制造》网页版（第 15 轮）

整本网页书：八篇三十一章，中英两版，42 个动画、虚拟实验与三维模型。问渠学习平台“教材”书架上标“网页版”，登录后阅读。将来按问渠教材格式（`textbook/<书>/book.yaml`）逐章改写（第 15 轮第 2 步，另写细则）。

## 目录

| 位置 | 内容 |
|---|---|
| `book.py` | 篇、章的中英文标题与要点（全书目录由它生成） |
| `src/zh/chNN.html`、`src/en/chNN.html` | 各章正文片段（只是 `<main class="chapter">` 里的内容；页头、侧栏目录、翻页由 `build.py` 生成） |
| `src/zh/labs/*.html`、`src/en/labs/*.html` | 虚拟实验、动画、三维模型（每个是自成一体的网页） |
| `img/*.webp`、`img/en/*.webp` | 插图（中文版、英文版） |
| `res_zh.json`、`res_en.json` | “互动资源”页的清单 |
| `style.html`、`script.html`、`script_index.html` | 公共样式与脚本 |
| `figsrc/` | 插图的生成程序与算例程序（Python、HTML 图源） |
| `GLOSSARY.md`、`PLATFORM.md` | 中英术语表；第 19–22、27 章共用设定（电控原型平台 WQ-SC） |

## 构建

```bash
python3 build.py out          # 生成到 out/（index.html、chNN.html、en/、labs/、img/、book.json）
cd out && python3 -m http.server 8000   # 浏览器打开 http://localhost:8000
```

CI（`.github/workflows/deploy.yml` 的 `webeditions` 任务）构建到 `textbook/build/sewing/webed/`，部署到服务器 `/opt/wenquest/textbook/sewing/webed/`，网关经 `/api/v1/textbook-web/<令牌>/...` 提供给登录用户。

## 改书

- 改正文：改 `src/zh/chNN.html`（英文同步改 `src/en/chNN.html`），推送 main 即上线。
- 加插图：图片转成 WebP 放 `img/`（英文版放 `img/en/`，同名），正文里照旧写 `img/名字.png`，构建时自动换成 `.webp`；英文页有英文图时自动用英文图。
- 章节编号、篇名：改 `book.py`。

## 课程包（第 16 轮）

`course/`：由本书开成的问渠机器人学院课程（31 讲）。`course/lessons/chNN.json` 是每讲内容（格式 `course/FORMAT.md`），`course/tools/check.py all` 检查，`course/tools/build_course.py <输出目录>` 生成讲义、课件、实验指导书、测验与发布清单。CI 生成到 `textbook/build/sewing/course/`，管理员在平台“管理 → 课程包”发布。说明见 `docs/帮助/从课程包建课.md`。
