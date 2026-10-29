# 缝纫机设计软件的网页互动帮助（第 49 轮）

一份源文件，生成两份帮助：

| 生成 | 上线地址 | 怎么打开 |
|---|---|---|
| `apps/web/src/static/help/sewing/index.html` | learn.wenquestrobotics.com/static/help/sewing/ | 软件右上角“？帮助”（按当前页签跳到对应一节） |
| `apps/web/src/static/help/sewing-freecad/index.html` | learn.wenquestrobotics.com/static/help/sewing-freecad/ | 网页版帮助左栏“看 FreeCAD 版帮助” |
| `services/gateway/app/sewcore/freecad/help/` | 随 FreeCAD 工作台安装包（离线） | 工作台工具栏“帮助” |

视频、封面、字幕只有一份：`apps/web/src/static/help/media/`（`web-*` 网页版录屏，`fc-*` FreeCAD 录屏）。离线版只带 `fc-*`。

## 改内容

1. 改 `sections/` 下的 Markdown：`common/` 两份都有，`web/`、`freecad/` 各自的。章节顺序在 `build.py` 的 `EDITIONS`。每个文件开头写 `id`、`title`、`lead`。
2. 文中的数一律写成 `{{键}}`，由 `build.py` 的 `numbers()` 从计算核心算（不手写数）。CAE 的真实结果在 `data/`：`web_cae.json`（`tools/collect_cae.py` 在本地完整环境里调网页版同一接口重算）、`crank_fea.json`（`tools/fem_crank_freecad.py` 在 FreeCAD 1.0.2 里用自带 Gmsh + CalculiX 算）。
3. 运行：`python3 docs/帮助/缝纫机软件帮助/build.py`（要 `pip install markdown`），再推送。

指令（单独一行）：

| 写法 | 生成 |
|---|---|
| `::anim{id=fea}` | 动画（`anim.js` 里的 `A.fea`）：arch、aiguard、fea、fatigue、modal、mbd、topo、family、extract |
| `::calc{id=speed}` | 小计算器（直接调 `/api/v1/sewing/analyze`，来宾也能用；离线版提示去在线版） |
| `::video{src=web-03-ai title="…"}` | 录像（mp4 + 封面 jpg + 中文字幕 vtt） |
| `::try{label="…" machine=lockstitch tab=checks p='{"n":6000}'}` | “试一试”按钮：带参数打开软件（`?machine=&tab=&p=`） |
| `::only{web}` … `::end` | 只在某一份里出现的段落 |

版式在 `template.html`（左栏目录随滚动高亮、搜索、深浅色、打印、代码块“复制”）。

## 重录视频

- 网页版：`tools/web-rec/`（Playwright 录屏 + `finish.py` 剪掉等待段、压 720p、写字幕）。要先起本地完整环境（`tools/local/`）和数字工厂 cae、hub（本轮在 `/home/claude/local/up.sh` 里），网关用 `WQ_AI_PROVIDER=none` 录 AI（画面上标“规则版”）。
- FreeCAD：`tools/freecad-rec/`（FreeCAD 1.0.2 AppImage 解包、Xvfb 虚拟显示器、`drive.py` 按时间表在界面里操作、ffmpeg 录屏、`fcfinish.py` 出片）。

## 规矩

- 没做的不写成做了；示意的标“示意”（模态振型、零件族动画），真算的写清楚是谁算的、哪天算的。
- 只写软件名，不写企业客户名、品牌名。
