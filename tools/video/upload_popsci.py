"""把一期白板科普传到 YouTube（第 80 轮 Q5，Eddie 11-04“好的”）：每期做完自动上传，进播放列表“问渠白板科普” / “WenQuest Whiteboard Science”。

    python3 tools/video/upload_popsci.py <科普目录> <MP4> [--privacy public]

<科普目录> 是 samples/白板讲课/每日科普/<日期>_<中文|英文>_<题目>/（读 lesson.json 的 title、title_en 和 字幕.srt）；
封面取 MP4 第 2 秒的画面（ffmpeg）。上传、加播放列表用 upload_youtube.py 的同一段程序（同一组 YT_* 密钥）。
注意：谷歌审核通过前，接口上传的视频会被锁成私密，要 Eddie 在 YouTube Studio 里点公开；公开后第二天自动出现在官网首页。
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PLAYLIST = {"zh": "问渠白板科普", "en": "WenQuest Whiteboard Science"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("mp4")
    ap.add_argument("--privacy", default="public", choices=["private", "unlisted", "public"])
    a = ap.parse_args()
    d = Path(a.dir)
    lesson = json.loads((d / "lesson.json").read_text(encoding="utf-8"))
    zh = "_中文_" in d.name
    lang = "zh" if zh else "en"
    title = lesson["title"] if zh else (lesson.get("title_en") or lesson["title"])
    desc = (f"{title}\n\n问渠白板科普：每天一期，三分钟，借热点讲一个科学道理。\n配音：AI 合成。\n问渠机器人学院 https://wenquestrobotics.com"
            if zh else
            f"{title}\n\nWenQuest Whiteboard Science: a three-minute science short every day, sparked by the news.\n"
            "Voice: AI-synthesized.\nWenQuest Robotics Academy https://wenquestrobotics.com")
    tags = ["科普", "白板动画", "问渠", "WenQuest"] if zh else ["science", "whiteboard animation", "explainer", "WenQuest"]
    with tempfile.TemporaryDirectory() as t:
        o = Path(t)
        shutil.copy(a.mp4, o / "lecture.mp4")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "2", "-i", str(o / "lecture.mp4"), "-frames:v", "1",
                        "-vf", "scale=1280:-2", str(o / "cover_youtube.png")], check=True)
        if (d / "字幕.srt").exists():
            shutil.copy(d / "字幕.srt", o / "lecture.srt")
        (o / "upload.json").write_text(json.dumps({"title": title, "description": desc, "tags": tags, "lang": lang,
                                                    "playlist": PLAYLIST[lang]}, ensure_ascii=False), encoding="utf-8")
        from upload_youtube import upload
        upload(o, a.privacy, None)


if __name__ == "__main__":
    main()
