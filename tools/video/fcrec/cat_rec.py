"""把几段录屏接成一个片段，字幕跟着接（第 20 课：官方 FreeCAD 一段 + 问渠 CAD 一段）。
    python3 cat_rec.py 输出.mp4 第一段.mp4 第二段.mp4 …    （每段旁边同名 .vtt）"""
import re
import subprocess
import sys
from pathlib import Path


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout)


def ts(x):
    return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:06.3f}"


def sec(t):
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def main(out, *parts):
    parts = [Path(p) for p in parts]
    inputs = sum([["-i", str(p)] for p in parts], [])
    chain = "".join(f"[{i}:v]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0[v]"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", chain, "-map", "[v]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], check=True)
    cues, off = [], 0.0
    for p in parts:
        v = p.with_suffix(".vtt")
        if v.exists():
            for a, b, txt in re.findall(r"(\d\d:\d\d:\d\d\.\d+) --> (\d\d:\d\d:\d\d\.\d+)\n(.+?)(?:\n\n|\n*$)", v.read_text(encoding="utf-8"), re.S):
                cues.append(f"{ts(sec(a) + off)} --> {ts(sec(b) + off)}\n{txt.strip()}")
        off += dur(p)
    Path(out).with_suffix(".vtt").write_text("WEBVTT\n\n" + "\n\n".join(cues) + "\n", encoding="utf-8")
    print("cat", len(parts), "parts", round(off, 1), "s", len(cues), "cues")


if __name__ == "__main__":
    main(*sys.argv[1:])
