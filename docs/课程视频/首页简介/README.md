# 首页模块视频简介（第 86 轮）

每段 1～2 分钟，中英两版（平台 AI 声音，第 86 轮 11-05 改）：英文版传 YouTube、挂美国官网；中文版投 B 站、挂国内版官网。
每段先写《讲稿》给 Eddie 审。画面是真界面截图做成的演示稿（要点逐条出现、黄框圈出、推近），做法见下。

| 编号 | 简介 | 挂到首页哪些卡 | 状态 |
|---|---|---|---|
| 01 | 问渠全貌 | 首页顶部 | 样片已出，待 Eddie 看 |
| 02 | 学习平台与 AI 建课 | 学习平台、AI 建课、课程目录 | 样片已出，待 Eddie 看 |
| 07 | 数字工厂 | 进入数字工厂、工厂演示、三维工厂、数字工厂实验 | 样片已出，待 Eddie 看 |
| 17 | 评价系统与校情中枢 | 评价系统、校情中枢 | 样片已出，待 Eddie 看 |

其余各段见《实施细则 · 第 86 轮》第三节。

## 怎么做一段

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
