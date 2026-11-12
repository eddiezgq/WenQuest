# 白板讲课（第 35 轮）

一节课 = 讲稿分段（带录音时间）+ 几张画板（每个元素写明在第几段讲稿时画）。`wb.py` 把它编成：

- `白板课.html`：网页版，单个文件、可离线打开；播放、拖进度、字幕、全屏；
- `白板课.mp4`：1920×1080、30 帧/秒，配原录音（`--mp4`）；
- `board.excalidraw`：同一套画板的 Excalidraw 文件（每张画板是一个 frame），第 2 步在平台里编辑用。

画法：方框、椭圆、箭头用 rough.js（Excalidraw 同款手绘线，MIT）；中文字用霞鹜文楷、英文用 Caveat（都是 OFL 开源字体），转成笔画路径后“先描边再填色”；简笔画图标在 `icons.py`（本项目自己画的线稿）。`player.js` 只按时间决定画面，网页播放和逐帧出视频用同一份代码。

依赖：Python 包 fonttools、brotli、playwright，ffmpeg。

    python3 tools/whiteboard/wb.py <课目录> [--mp4]
    python3 tools/whiteboard/snap.py <课目录> [秒 …]     # 每张画板画完时的截图，检查排版

样例：`samples/白板讲课/物理学导论/`（Eddie 原视频的录音）。

## 平台上（第 35 轮第 3 步）

核心代码在网关 `services/gateway/app/production/whiteboard/`（编译、AI 写稿排板、声音处理），老师的白板课由 `app/whiteboards.py`（存储、后台生成、出 MP4）和 `app/whiteboard_api.py`（接口）管理；编辑器源码在 `apps/web/wb-editor/`（网页端镜像打包到 `/wb-editor/`）。这里的 `wb.py` 只用于本机做样片。使用说明见 `docs/帮助/白板课使用说明.md`。

## 三维简画讲故事（第 162 轮）

手绘线条的三维人物在三维场景里走动、说话、做事，镜头推拉摇移，用来讲工作场景的小故事（机构、零件动画仍用三维模型、Blender、Manim）。

- 播放器：`services/gateway/app/production/whiteboard/scene3d.js`（人物骨架与约 25 种姿势、表情、发型和衣着；道具和场景；镜头；对话气泡与旁白字幕；每个镜头开头一笔一笔画出来）。
- 故事：`<故事目录>/story.yaml`——演员（外形、声音）、场景（道具清单）、镜头（机位关键帧、人物站位、每一拍谁说什么、谁做什么）。时间全部按配音长度自动排。
- 出片：

      WQ_TTS_MODELS=<kokoro 模型目录> python3 tools/whiteboard/story.py <故事目录> [--mp4] [--snap 秒,秒]

  输出在 `<故事目录>/out/`（不进仓库）：`story.html`（网页版，暂停时可拖动画面转视角）、`story.mp4`（1280×720，30 帧/秒，每帧约 0.1 秒）。
- 样片：`samples/白板讲课/三维故事/老板不在的那一周/`（原创人物与情节，AI 配音）。
