# 首页模块视频简介（第 86 轮）

每段 1～2 分钟，中英两版（平台 AI 声音，第 86 轮 11-05 改）：英文版传 YouTube、挂美国官网；中文版投 B 站、挂国内版官网。
每段先写《讲稿》给 Eddie 审。画面是真界面截图做成的演示稿（要点逐条出现、黄框圈出、推近），做法见下。

| 编号 | 简介 | 挂到首页哪些卡 | 状态 |
|---|---|---|---|
| 01 | 问渠全貌 | 首页顶部 | 讲稿待审 |
| 02 | 学习平台与 AI 建课 | 学习平台、AI 建课、课程目录 | 讲稿待审；要先在本机测试环境截学习平台界面 |
| 07 | 数字工厂 | 进入数字工厂、工厂演示、三维工厂、数字工厂实验 | `07-数字工厂/` 样片出片中 |
| 17 | 评价系统与校情中枢 | 评价系统、校情中枢 | `17-评价与校情/` 样片出片中 |

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
