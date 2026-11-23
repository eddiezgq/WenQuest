"""3-minute course overview (wenquest-cad course plan section 13, item 3): cut from the published lesson recordings.

Clips are chosen by subtitle cue numbers, so the Chinese and English recordings (same script, different
timings) give the same pieces. Subtitles only, no voice (Eddie 11-23). Writes wqcad-intro{,-en}.mp4/.jpg/.vtt
next to the lesson media.

    python3 tools/video/fcrec/overview.py
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

MEDIA = Path(__file__).resolve().parents[3] / "apps/web/src/static/help/wqcad/media"

# (segment, first cue, cue after the last one or None = to the end, zh caption, en caption)
CLIPS = [
    ("l01b", 2, 6, "第 1 课 界面：鼠标平移、旋转、缩放，看整台 WQ-LS 平缝机",
     "Lesson 1 The window: pan, rotate and zoom the whole WQ-LS sewing machine"),
    ("l04c", 2, None, "第 4 课 约束：尺寸约束把草图定死，凸台做出针夹",
     "Lesson 4 Constraints: dimensions fully constrain the sketch, then a pad makes the needle clamp"),
    ("l09b", 2, None, "第 9 课 阵列：一道槽环形阵列成 48 道，手轮做成",
     "Lesson 9 Patterns: one groove becomes 48 with a polar pattern"),
    ("l13b", 4, None, "第 13 课 曲面：轮廓两头加相切，折棱（G0）变顺滑（G1）",
     "Lesson 13 Surfaces: tangency at the ends of the outline turns a crease (G0) into a smooth blend (G1)"),
    ("l16b", 7, 11, "第 16 课 多体动力学：5000 r/min 时上轴要多大力矩、曲柄销受多大力",
     "Lesson 16 Multibody dynamics: drive torque and crank-pin force at 5000 r/min"),
    ("l18b", 9, None, "第 18 课 工程图：装配图、明细表、零件序号，导出 PDF",
     "Lesson 18 Drawings: assembly drawing, parts list, balloons, export to PDF"),
    ("l19a", 11, 14, "第 19 课 有限元：曲柄的应力，核查通过才给安全系数",
     "Lesson 19 FEA: stress in the crank; a safety factor only when the checks pass"),
    ("l21c", 8, 11, "第 21 课 AI 工作台：AI 起草，代码校核，人拍板",
     "Lesson 21 AI workbench: AI drafts, code checks, a person decides"),
]
OPENING = ("问渠 CAD 培训课程：21 课，从界面、草图讲起，一课一课做出平缝机 WQ-LS 的零件",
           "WenQuest CAD training course: 21 lessons, from the window and sketches up, making the parts of the WQ-LS sewing machine")
CLOSING = ("录屏都在各课里，点左边目录开始第 1 课", "All the recordings are in the lessons; start with lesson 1 in the contents on the left")


def cues(vtt: Path) -> list[float]:
    t = vtt.read_text(encoding="utf-8")
    return [int(h) * 3600 + int(m) * 60 + float(s) for h, m, s in re.findall(r"(\d+):(\d+):(\d+\.\d+) -->", t)]


def duration(mp4: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "0", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def ts(x: float) -> str:
    return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:06.3f}"


def make(sfx: str) -> None:
    en = sfx == "-en"
    spans = []
    for seg, a, b, zh, eng in CLIPS:
        mp4, vtt = MEDIA / f"wqcad-{seg}{sfx}.mp4", MEDIA / f"wqcad-{seg}{sfx}.vtt"
        c = cues(vtt)
        start = c[a]
        end = c[b] if b is not None else duration(mp4)
        spans.append((mp4, start, end, eng if en else zh))
    with tempfile.TemporaryDirectory() as tmp:
        parts = []
        for i, (mp4, s, e, _) in enumerate(spans):
            p = Path(tmp) / f"{i}.mp4"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", str(mp4),
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "25", "-an", str(p)],
                           check=True)
            parts.append(p)
        lst = Path(tmp) / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts), encoding="utf-8")
        out = MEDIA / f"wqcad-intro{sfx}.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c:v", "libx264", "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        "-an", str(out)], check=True)
        lens = [duration(p) for p in parts]
    # subtitles: opening line over the first 8 s, then one line per clip, closing line over the last 6 s (reading time)
    lines, t = [], 0.0
    for k, ((_, _, _, cap), d) in enumerate(zip(spans, lens)):
        a, b = t, t + d
        if k == 0:
            lines.append((0.0, 8.0, OPENING[1] if en else OPENING[0]))
            a = 8.0
        if k == len(spans) - 1:
            lines.append((a, b - 6.0, cap))
            lines.append((b - 6.0, b, CLOSING[1] if en else CLOSING[0]))
        else:
            lines.append((a, b, cap))
        t = b
    vtt = "WEBVTT\n\n" + "".join(f"{ts(a)} --> {ts(b)}\n{x}\n\n" for a, b, x in lines)
    (MEDIA / f"wqcad-intro{sfx}.vtt").write_text(vtt, encoding="utf-8")
    poster_at = sum(lens[:4]) + lens[4] * 0.8          # multibody dynamics curves
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{poster_at:.2f}", "-i", str(out), "-frames:v", "1",
                    "-vf", "scale=960:-2", "-q:v", "4", str(MEDIA / f"wqcad-intro{sfx}.jpg")], check=True)
    print(out.name, f"{t:.1f} s", f"{out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    for sfx in ("", "-en"):
        make(sfx)
