# 缝纫机设计软件的网页互动帮助（第 49 轮；典型案例第 52 轮）

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
| `::anim{id=fea}` | 动画（`anim.js` 里的 `A.fea`）：arch、aiguard、fea、fatigue、modal、mbd、topo、family、extract、explode（整机拆装，第 52 轮） |
| `::calc{id=speed}` | 小计算器（直接调 `/api/v1/sewing/analyze`，来宾也能用；离线版提示去在线版） |
| `::video{src=web-03-ai title="…"}` | 录像（mp4 + 封面 jpg + 中文字幕 vtt） |
| `::try{label="…" machine=lockstitch tab=checks p='{"n":6000}'}` | “试一试”按钮：带参数打开软件（`?machine=&tab=&p=`） |
| `::only{web}` … `::end` | 只在某一份里出现的段落 |

版式在 `template.html`（左栏目录随滚动高亮、搜索、深浅色、打印、代码块“复制”）。

## 典型案例（第 52 轮）

五个案例 `sections/common/case-*.md`（总览 `cases.md`；案例五电脑横机第 54 轮加）里的数全部来自 `data/cases.json`，文中写成路径：`{{ls.crank_fea.vm}}`（`ls` 平缝、`ol` 包缝、`cv` 绷缝、`pt` 花样、`fk` 横机），派生的数（百分比、表格、刀具清单）在 `build.py` 的 `case_numbers()` 里算。

- **`tools/run_cases.py`**：用网页版同一套接口把四个案例从头跑到尾（有限元、疲劳、减重与复核、数控、动力学、电机选型、机壳模态、设计优化交给数字工厂计算服务；不联网的校核直接调计算核心），写 `data/cases.json`，并把案例用的简化机壳 STEP 写到 `media/case-ls-frame.step` 给读者下载。也是回归检查：改了计算核心，重跑（`--check` 只跑不写），再 `build.py`，帮助里的数跟着变；结论变了就要改案例的文字。要起本地完整环境和数字工厂 cae、hub；一次要二十来个计算任务，hub 的每日上限要调高：`WQ_DESIGN_SW_DAILY=500 WQ_DESIGN_SW_OPT_DAILY=50`。中途会在本单位零件库里临时录一台示例电机 SV-3000H，跑完删掉。
- **`tools/explode_data.py`**：整机拆装动画的数据。读教材平缝机虚拟样机的三维模型（`textbook/web-editions/sewing/models/proto_lockstitch.py`，27 个零件编号），按样机的机构库摆到主轴 0°，投影成斜视图取每个零件的外轮廓，写 `data/explode.json`（约 12 KB）。
- 录屏：网页版 `tools/web-rec/w09.js`–`w13.js`（`web-09-case-ls` … `web-13-case-fk`），FreeCAD `drive.py` 的 `fc-07-case-ls`。`rec.js` 加了 `choose`（选项参数）、`api`（幕后调接口）、`job`（等 CAE 算完、剪掉等待、点开结果）。

## 重录视频

- 网页版：`tools/web-rec/`（Playwright 录屏 + `finish.py` 剪掉等待段、压 720p、写字幕）。要先起本地完整环境（`tools/local/`）和数字工厂 cae、hub（本轮在 `/home/claude/local/up.sh` 里），网关用 `WQ_AI_PROVIDER=none` 录 AI（画面上标“规则版”）。
- FreeCAD：`tools/freecad-rec/`（FreeCAD 1.0.2 AppImage 解包、Xvfb 虚拟显示器、`drive.py` 按时间表在界面里操作、ffmpeg 录屏、`fcfinish.py` 出片）。往 Python 控制台打命令用“逐字插入”，不用模拟按键（虚拟显示器的键盘布局会把 `;`、`=` 打错）。

## 规矩

- 没做的不写成做了；示意的标“示意”（模态振型、零件族动画），真算的写清楚是谁算的、哪天算的。
- 只写软件名，不写企业客户名、品牌名。
