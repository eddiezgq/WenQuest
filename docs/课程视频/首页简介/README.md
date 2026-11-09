# 首页模块视频简介（第 86 轮）

每段 1～2 分钟，中英两版（平台 AI 声音，第 86 轮 11-05 改）：英文版传 YouTube、挂美国官网；中文版投 B 站、挂国内版官网。
每段先写《讲稿》给 Eddie 审。**第 127 轮起新做法：网页版 PPT + 真页面录屏，不用截图**（《实施细则 · 第 127 轮》，样页在 `样页/`），见下“新做法”；01–17 段仍是第 86 轮的截图演示稿（做法见“怎么做一段（旧做法）”），Eddie 看过新做法的 07、18 再定要不要重出。

| 编号 | 简介 | 挂到首页哪些卡 | 状态 |
|---|---|---|---|
| 01 | 问渠全貌 | 首页顶部 | 样片已出，待 Eddie 看 |
| 02 | 学习平台与 AI 建课 | 学习平台、AI 建课、课程目录 | 样片已出，待 Eddie 看 |
| 07 | 数字工厂（四座厂；第 127 轮新做法） | 进入数字工厂、工厂演示、三维工厂、数字工厂实验 | 新做法样片已出，待 Eddie 看 |
| 17 | 评价系统与校情中枢 | 评价系统、校情中枢 | 样片已出，待 Eddie 看 |
| 18 | 电子与芯片（第 101 轮讲稿；第 127 轮新做法） | 电子与芯片一组 | 新做法样片已出，待 Eddie 看 |

其余各段见《实施细则 · 第 86 轮》第三节。

## 新做法：网页版 PPT + 真页面录屏（第 127 轮）

一句配音配一个镜头，两种画面：

- **讲道理的句子 → 网页版 PPT**（讲稿 `kind: page`）。在 `<段>/课件/ppt.html` 里写各页的 `<section class="pg">`（HTML + SVG 矢量图，风格同 `样页/`：
  深底、黄色强调、线稿图标；中文版中文标题 + 英文小字，英文版只出英文），写法见 `tools/video/intro_ppt.py` 开头：`data-k` 第几个“>”出现、
  `data-d` 同一步里晚几毫秒、`data-a="draw"` 线条画出来、`class="sub"` 中文版里的英文小字、`data-en` 英文版换成的文字。
  `python3 tools/video/intro_ppt.py <段>` 写出 `课件/index.zh.html`、`index.html`。图都是**示意**，不画假界面。
- **看真东西的句子 → 真页面录屏**（讲稿 `kind: rec`，`clip:` 或 `clip_zh` / `clip_en`）。在 `<段>/录屏.yaml` 写每段录什么
  （页面、开录前的准备、第几秒点哪儿 / 填什么 / 滚到哪儿 / 黄圈圈哪儿、要剪掉的等待），本机起好服务后
  `WQ_PROXY=eda=8150 python3 tools/video/screenrec.py <段> [--only 名字]` 录成 `录屏/<名字>.mp4`（1920×1080、30 帧、H.264）。
  写法见 `tools/video/screenrec.py` 开头。数字工厂界面只有中文，录一段两种语言共用；官网、问渠电子按语言各录一段（`langs: [zh, en]`）。
  录法：Chrome screencast 收帧（JPEG 95），不用 Playwright 的 recordVideo（码率低、文字糊）；`viewport: [1440, 810]` 这类小视口 = 页面放大后按设备像素渲染，文字清楚。
- 出片时 `make.py` 把录屏按这句配音的长度整体放慢或加快（0.8～1.25 倍），还不够长就停在最后一帧，太长就截掉——所以录屏长度按配音估（中文约每秒 4 字）。
- 本机要起的服务（18 段）：PostgreSQL、MQTT 总线、电路板厂的 mock_erpnext + 枢纽（8142，`WQ_PLANT_FILE=factory/plants/wenquest-pcb.yaml`、
  `WQ_CAE_URL=http://127.0.0.1:8200`）+ sim（起法同下面旧做法第 2 步）；计算服务 `cd factory/digital && WQ_CAE_DATA=<临时目录> uvicorn cae.service:app --port 8200`
  （电路分析、虚拟仪器要）；功能测试台要先有做过功能测试的板（Node-RED 桥接 `factory/digital/bridge` 起好，`python3 tests/plant_loop.py --hub … --erp … --item DRV-JOINT:3`）；
  问渠电子 `cd services/eda && pip install -r requirements.txt && WQ_GATEWAY_URL=http://127.0.0.1:9 uvicorn app:app --port 8150`。工厂网页先 `npm run build`（`factory/digital/web`）。
- 检查：浏览器打开 `课件/index.zh.html` 逐页看；录屏逐段抽帧看（`ffmpeg -i 录屏/x.mp4 -vf fps=2,tile=4x4 -frames:v 1 x.jpg`）；
  `make.py --voice estimate` 无声试看，每句抽一帧看；然后 Actions 出片（同下第 5 步）。

## 怎么做一段（旧做法：截图演示稿，01–17 段）

1. 写 `<编号-名称>/讲稿.yaml`（格式见 `tools/video/intro_deck.py` 开头的说明；`capture` 列要截的界面）。
2. 截图：`python3 tools/video/intro_shots.py <目录>`。官网页面直接从 `site/` 截；数字工厂页面（`hub:` 写端口）要先在本机起教学版数字工厂：
   PostgreSQL（`pg_ctlcluster 16 main start`）、MQTT 总线（`pip install amqtt`，配置里开 1883 和网页用的 9001）、`mock_erpnext`（8091）、
   `uvicorn hub.app:app --port 8140`（环境变量 `WQ_DB`、`WQ_MQTT_HOST/PORT`、`WQ_MODE=teach`、`WQ_AUTH=local`、`WQ_SECRET`、`WQ_ERPNEXT_URL`）和
   `sim/main.py`（`WQ_SIM_SPEED=60`），等一两分钟实验 7 情景跑起来再截；机器人厂另起一套（总线 1884、端口 8141、`WQ_PLANT_FILE=factory/plants/wenquest-robot.yaml`）。
   数字工厂界面只有中文，英文版用同一张图。
3. 演示稿：`python3 tools/video/intro_deck.py <目录>`（检查每页的“>”数和 steps 数对得上）。浏览器打开 `课件/index.zh.html` 可以翻页看。
4. 本机试看：`python3 tools/video/make.py <目录> --lang zh --voice estimate --out /tmp/v`（无声，按字数估时长）。
5. 出片：GitHub → Actions →“Lecture videos 公开课视频”：task `render`、lectures 填目录、voice `kokoro`、lang `both`。成片在运行的下载页。
   学习平台页面（`learn:` 写路径）要先搭本机完整环境：`tools/local/setup.sh`，导入样例课 `python3 /home/claude/local/import_physics.py && php /home/claude/local/enrol.php 2`；
   AI 建课的两个项目用 `teacher1` 通过网关接口建（上传 `samples/大学物理/课程资料`、开始、回答问题、确认资料清单），项目号写进讲稿。

## YouTube（2026-11-05 私密上传，Eddie 在 Studio 看过后公开；播放列表“问渠产品介绍 / WenQuest product tours”）

| 段 | 英文版 | 中文版 | catalog.yaml 键 |
|---|---|---|---|
| 01 问渠全貌 | spCHVOw97v8 | 2C8JdfSlyTU | overview |
| 02 学习平台与 AI 建课 | XB0CTTIXoWM | 1eycQZx_36I | learn |
| 03 教材与课件 | rusMo87KWK0 | fNcqT09_jFg | textbook |
| 04 白板课 | F90JgWGEtNQ | lcQbS0G_qMw | whiteboard |
| 05 三维仿真视频 | dlyDt47ccF4 | QH-LMrs3988 | video3d |
| 07 数字工厂 | jXvQ3KIRwtQ | JWw5kZ60Nvc | factory |
| 15 凸轮与轴承 | MTKbcIgE6to | nTKZ9k5MX-I | cambearing |
| 16 虚拟实验室 | GzjaMcvmaCY | xOpQ6uuCPCc | labs |
| 17 评价与校情 | v6R-rRzFWsw | hGESSq2LjCc | eval |

美国官网用英文版编号（Eddie 公开后填进 `tools/site_home/catalog.yaml` 的 `intro.*.yt`）；国内版官网用 B 站 BV 号（`bv`，B 站投稿资料见 `B站投稿资料.md`）。
