# 问渠演示视频 · 制作脚本

成品：6 分多钟中文演示视频（1920×1080，H.264 + AAC，烧录字幕，另附 .srt）。分镜与解说词以
`docs/宣传/2026-10_推介幻灯片与演示视频.md` 第二节为准；`narration.json` 逐句照抄（`say` 只改读法，不改字幕）。
画面全部来自本仓库的实际产出：平台页面、教材、Manim 动画、浏览器实验、数字工厂截图、实验指导书。

媒体不进仓库，放在一个工作目录（下称 `$W`）里。重建步骤：

1. 本地环境：`/home/claude/local/start-all.sh`（平台），`python3 -m http.server 8701`（在 `textbook/build`），
   `python3 -m http.server 8702`（在 `site/`）。
2. 配音：`python3 tts.py $W`（Kokoro 云夏 sid 51，语速 0.85，离线）。
3. 动画：`bash render_anims.sh $W`（4 段 1080p）。
4. 实验与官网录屏：`python3 record.py $W`（逐帧录制；三维实验约 10 分钟一段）。
5. 平台截图：`python3 capture_pages.py $W`；课程委员会截图用 `$W/../rev_committee.png`（2026-09-30 本地实测）。
6. 实验 12.1 的指导书与报告模板：`soffice --headless --convert-to pdf` 两个 docx（`textbook/build/robotics/lab/`），
   再 `pdftoppm -r 110 -png -f 1 -l 1`，放到 `$W/docs/`。
7. 合成：`python3 make_video.py $W`（约 20 分钟）；`--preview 30` 每秒一帧，快速检查画面。

输出：`$W/问渠演示视频.mp4`、`.srt`。分镜、每个镜头用的素材和标签都在 `make_video.py` 的 `storyboard()` 里。
