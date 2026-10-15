# 白板讲课样片（2026-10-15）

起因：Eddie 发来他以前用 VideoScribe 做的《物理学导论》视频（白底、手拿笔边讲边画、概念图一格一格长出来），问“你能帮我这样上课吗”。

这是 40 秒的技术样片，内容取自那段视频的“物理学在自然科学中的位置 → 七个领域”，再加一段机器人手臂受力（课程标准：实际问题以机器人为主）。

做法（全部自动、不用 VideoScribe）：
1. `beats.json`：分段讲稿，每段写好要画的东西。
2. `tts.py`：用平台自带的本地语音合成（Kokoro，男声“云健”）逐段配音，得到每段的起止时间 `times.json`。
3. `build.py`：把文字（霞鹜文楷手写楷体 + Caveat 手写英文，均为开源字体）转成笔画路径，方框、连线、机器人手臂画成略带手绘抖动的线条，按每段配音的时长排好“谁先画、画多久”，生成 `page.html`。
4. `page.html` 里一支马克笔跟着笔尖走；`render.py` 用无头浏览器逐帧截图（30 帧/秒），和配音合成 MP4。

依赖（不进仓库）：`../fonts/node_modules`（`npm i lxgw-wenkai-webfont@1.7.0 @fontsource/caveat`）、Kokoro 模型（`services/voice/fetch_models.sh`）。
